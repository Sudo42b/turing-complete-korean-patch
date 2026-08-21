// Turing Complete 한국어 패치 설치기.
//
// 게임 번역 ID 는 영문 원문의 해시라서, 게임이 원문이나 로컬라이제이션
// 네임스페이스를 손대면 통째로 바뀐다. 그래서 이 패처는 ID 를 박아두지 않고,
// 설치 시점에 게임이 배포한 원문 목록(translations/_ids_and_english.txt)을 읽어
// 영문 원문으로 대조해 Korean.txt 를 생성한다.
package main

import (
	"bufio"
	"bytes"
	_ "embed"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"regexp"
	"runtime"
	"strings"
)

//go:embed translation_dict.json
var dictJSON []byte

//go:embed NotoSansCJK-SC-Korean.otf
var koreanFont []byte

// 게임은 언어별로 폰트를 고른다: Japanese -> JP, Chinese (Traditional) -> TC, 그 외 -> SC.
// 한국어도 SC 로 떨어진다. Noto Sans CJK SC 는 게임 동봉 Noto Sans SC 의 상위 집합이라
// 교체해도 중국어 간체 표시가 유지된다.
var fontTargets = []string{"NotoSansSC_Regular.ttf", "NotoSansSC_Bold.ttf"}

const steamSubPath = "steamapps/common/Turing Complete"

var (
	sectionRe = regexp.MustCompile(`^=== (.*) ===\s*$`)
	entryRe   = regexp.MustCompile(`^\$(\d+)\*(.*)$`)
	vdfPathRe = regexp.MustCompile(`"path"\s+"([^"]+)"`)

	// 줄 첫머리의 # 는 뒤따르는 항목에 붙는 주석이다. 본문의 리터럴 # 는 \# 로
	// 이스케이프되므로 영향받지 않는다.
	commentRe = regexp.MustCompile(`^#`)
)

type entry struct {
	section string
	id      string
	text    string
}

type dictFile struct {
	Map map[string]string `json:"map"`
}

func main() {
	restore := len(os.Args) > 1 && (os.Args[1] == "-restore" || os.Args[1] == "--restore")

	fmt.Println("========================================")
	fmt.Println("  Turing Complete 한국어 패치")
	fmt.Println("========================================")
	fmt.Println()

	gameDir := findGameDir()
	if gameDir == "" {
		fmt.Println("[!] 게임 경로를 자동으로 찾지 못했습니다.")
		fmt.Print("    게임 폴더 경로를 직접 입력하세요: ")
		reader := bufio.NewReader(os.Stdin)
		line, _ := reader.ReadString('\n')
		gameDir = strings.Trim(strings.TrimSpace(line), `"`)
	}
	if !isGameDir(gameDir) {
		fmt.Printf("[오류] 올바른 게임 폴더가 아닙니다: %s\n", gameDir)
		fmt.Println("       translations/ 와 asset/font/NotoSansSC_Regular.ttf 가 있어야 합니다.")
		waitAndExit(1)
	}
	fmt.Printf("[*] 게임 경로: %s\n\n", gameDir)

	if restore {
		if err := restoreFonts(gameDir); err != nil {
			fmt.Printf("[오류] 복구 실패: %v\n", err)
			waitAndExit(1)
		}
		if err := os.Remove(filepath.Join(gameDir, "translations", "Korean.txt")); err == nil {
			fmt.Println("[+] Korean.txt 삭제")
		}
		fmt.Println()
		fmt.Println("원본으로 복구했습니다.")
		waitAndExit(0)
	}

	refs, source, err := loadReference(gameDir)
	if err != nil {
		fmt.Printf("[오류] %v\n", err)
		waitAndExit(1)
	}
	fmt.Printf("[*] 원문 목록: %s (%d개 항목)\n", source, len(refs))

	var dict dictFile
	if err := json.Unmarshal(dictJSON, &dict); err != nil {
		fmt.Printf("[오류] 번역 사전을 읽지 못했습니다: %v\n", err)
		waitAndExit(1)
	}

	translated := make([]entry, 0, len(refs))
	for _, e := range refs {
		if ko, ok := dict.Map[normalize(e.text)]; ok {
			translated = append(translated, entry{e.section, e.id, ko})
		}
	}
	pct := 0.0
	if len(refs) > 0 {
		pct = float64(len(translated)) * 100 / float64(len(refs))
	}
	fmt.Printf("[*] 사전 %d개와 대조 -> %d개 번역 (%.1f%%), 미번역 %d개\n",
		len(dict.Map), len(translated), pct, len(refs)-len(translated))

	transPath := filepath.Join(gameDir, "translations", "Korean.txt")
	if err := os.WriteFile(transPath, dumpTranslations(translated), 0644); err != nil {
		fmt.Printf("[오류] Korean.txt 설치 실패: %v\n", err)
		waitAndExit(1)
	}
	fmt.Print("[+] Korean.txt 설치 완료\n\n")

	fmt.Println("[*] 한글 폰트 적용 중 (게임 동봉 폰트에는 한글 글리프가 없습니다)...")
	if err := patchFonts(gameDir); err != nil {
		fmt.Printf("[!] 폰트 패치 실패: %v\n", err)
	}

	printDone()
}

// --- 게임 폴더 탐색 -------------------------------------------------------

func isGameDir(path string) bool {
	if path == "" {
		return false
	}
	if fi, err := os.Stat(filepath.Join(path, "translations")); err != nil || !fi.IsDir() {
		return false
	}
	_, err := os.Stat(filepath.Join(path, "asset", "font", fontTargets[0]))
	return err == nil
}

func steamRoots() []string {
	home, _ := os.UserHomeDir()
	var roots []string

	switch runtime.GOOS {
	case "windows":
		pf86 := os.Getenv("ProgramFiles(x86)")
		if pf86 == "" {
			pf86 = `C:\Program Files (x86)`
		}
		pf := os.Getenv("ProgramFiles")
		if pf == "" {
			pf = `C:\Program Files`
		}
		roots = []string{
			filepath.Join(pf86, "Steam"),
			filepath.Join(pf, "Steam"),
			filepath.Join(os.Getenv("LOCALAPPDATA"), "Steam"),
		}
	case "darwin":
		roots = []string{filepath.Join(home, "Library", "Application Support", "Steam")}
	default:
		roots = []string{
			filepath.Join(home, ".local", "share", "Steam"),
			filepath.Join(home, ".steam", "steam"),
		}
	}

	// libraryfolders.vdf 에 등록된 추가 라이브러리도 훑는다.
	const bs = "\u005c"
	seen := map[string]bool{}
	for _, r := range roots {
		seen[r] = true
	}
	for i := 0; i < len(roots); i++ {
		data, err := os.ReadFile(filepath.Join(roots[i], "steamapps", "libraryfolders.vdf"))
		if err != nil {
			continue
		}
		for _, m := range vdfPathRe.FindAllStringSubmatch(string(data), -1) {
			p := strings.ReplaceAll(m[1], bs+bs, bs)
			if !seen[p] {
				seen[p] = true
				roots = append(roots, p)
			}
		}
	}
	return roots
}

func findGameDir() string {
	for _, root := range steamRoots() {
		candidate := filepath.Join(root, filepath.FromSlash(steamSubPath))
		if isGameDir(candidate) {
			return candidate
		}
	}
	return ""
}

// --- 번역 파일 파싱/직렬화 -------------------------------------------------

// parseTranslations 는 게임 번역 파일 형식을 읽는다.
// idPrefixed 는 _ids_and_english.txt 처럼 본문 앞에 id 가 한 번 더 붙는 형식이다.
func parseTranslations(data []byte, idPrefixed bool) []entry {
	var entries []entry
	var section, curID string
	var buf []string
	haveEntry := false

	flush := func() {
		if !haveEntry {
			return
		}
		text := strings.TrimSpace(strings.Trim(strings.Join(buf, "\n"), "\n"))
		if idPrefixed && strings.HasPrefix(text, curID) {
			text = strings.TrimPrefix(text[len(curID):], " ")
		}
		entries = append(entries, entry{section, curID, text})
		haveEntry = false
	}

	sc := bufio.NewScanner(bytes.NewReader(data))
	sc.Buffer(make([]byte, 0, 64*1024), 4*1024*1024)
	for sc.Scan() {
		line := strings.TrimRight(sc.Text(), "\r")
		if commentRe.MatchString(line) {
			continue
		}
		if m := sectionRe.FindStringSubmatch(line); m != nil {
			flush()
			buf = nil
			section = m[1]
			continue
		}
		if m := entryRe.FindStringSubmatch(line); m != nil {
			flush()
			curID = m[1]
			buf = []string{strings.TrimLeft(m[2], " \t")}
			haveEntry = true
			continue
		}
		if haveEntry {
			buf = append(buf, line)
		}
	}
	flush()
	return entries
}

func dumpTranslations(entries []entry) []byte {
	var b strings.Builder
	lastSection := ""
	first := true
	for _, e := range entries {
		if e.section != lastSection {
			if !first {
				b.WriteString("\n\n")
			}
			first = false
			fmt.Fprintf(&b, "=== %s ===\n\n", e.section)
			lastSection = e.section
		}
		if strings.Contains(e.text, "\n") {
			fmt.Fprintf(&b, "$%s*\n%s\n", e.id, e.text)
		} else {
			fmt.Fprintf(&b, "$%s* %s\n", e.id, e.text)
		}
	}
	return []byte(b.String())
}

// normalize 는 원문 대조용 정규화 — 줄 끝 공백과 앞뒤 여백만 제거한다.
func normalize(text string) string {
	lines := strings.Split(strings.TrimSpace(text), "\n")
	for i, l := range lines {
		lines[i] = strings.TrimRight(l, " \t\r")
	}
	return strings.Join(lines, "\n")
}

// loadReference 는 현재 빌드의 id -> 영문 원문 목록을 읽는다.
func loadReference(gameDir string) ([]entry, string, error) {
	trans := filepath.Join(gameDir, "translations")

	if data, err := os.ReadFile(filepath.Join(trans, "_ids_and_english.txt")); err == nil {
		return parseTranslations(data, true), "_ids_and_english.txt", nil
	}
	// 대체 경로: _debug.txt 는 본문을 X...X 로 감싸 둔다.
	if data, err := os.ReadFile(filepath.Join(trans, "_debug.txt")); err == nil {
		entries := parseTranslations(data, false)
		for i := range entries {
			t := strings.TrimPrefix(entries[i].text, "X")
			t = strings.TrimSuffix(t, "X")
			entries[i].text = strings.TrimSpace(t)
		}
		return entries, "_debug.txt", nil
	}
	return nil, "", fmt.Errorf("번역 대조용 원문 목록을 찾지 못했습니다 " +
		"(translations/_ids_and_english.txt 또는 _debug.txt 필요)")
}

// --- 폰트 -----------------------------------------------------------------

func patchFonts(gameDir string) error {
	fontDir := filepath.Join(gameDir, "asset", "font")
	for _, name := range fontTargets {
		dest := filepath.Join(fontDir, name)
		fi, err := os.Stat(dest)
		if err != nil {
			fmt.Printf("[!] 폰트 대상 없음, 건너뜀: %s\n", name)
			continue
		}
		if fi.Size() == int64(len(koreanFont)) {
			fmt.Printf("[=] %s 이미 패치됨\n", name)
			continue
		}
		backup := dest + ".orig"
		if _, err := os.Stat(backup); os.IsNotExist(err) {
			if err := copyFile(dest, backup); err != nil {
				return fmt.Errorf("%s 백업 실패: %w", name, err)
			}
		}
		if err := os.WriteFile(dest, koreanFont, 0644); err != nil {
			return fmt.Errorf("%s 교체 실패: %w", name, err)
		}
		fmt.Printf("[+] %s 교체 완료 (원본 -> %s)\n", name, filepath.Base(backup))
	}
	return nil
}

func restoreFonts(gameDir string) error {
	fontDir := filepath.Join(gameDir, "asset", "font")
	for _, name := range fontTargets {
		dest := filepath.Join(fontDir, name)
		backup := dest + ".orig"
		if _, err := os.Stat(backup); err != nil {
			fmt.Printf("[!] 백업 없음, 건너뜀: %s\n", name)
			continue
		}
		if err := copyFile(backup, dest); err != nil {
			return err
		}
		os.Remove(backup)
		fmt.Printf("[+] %s 복구\n", name)
	}
	return nil
}

func copyFile(src, dst string) error {
	in, err := os.Open(src)
	if err != nil {
		return err
	}
	defer in.Close()
	out, err := os.Create(dst)
	if err != nil {
		return err
	}
	defer out.Close()
	if _, err := io.Copy(out, in); err != nil {
		return err
	}
	return out.Sync()
}

// --- 마무리 ---------------------------------------------------------------

func printDone() {
	fmt.Println()
	fmt.Println("==========================================")
	fmt.Println("  설치 완료!")
	fmt.Println()
	fmt.Println("  게임 실행 후:")
	fmt.Println("  Options > Language > 한국어 선택")
	fmt.Println()
	fmt.Println("  되돌리려면 -restore 옵션으로 실행하세요.")
	fmt.Println("==========================================")
	waitAndExit(0)
}

func waitAndExit(code int) {
	if runtime.GOOS == "windows" {
		fmt.Println()
		fmt.Println("아무 키나 누르면 종료됩니다...")
		bufio.NewReader(os.Stdin).ReadString('\n')
	}
	os.Exit(code)
}
