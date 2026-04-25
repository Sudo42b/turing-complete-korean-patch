package main

import (
	"bytes"
	_ "embed"
	"encoding/binary"
	"fmt"
	"os"
	"path/filepath"
	"runtime"
	"strings"
)

//go:embed Korean.txt
var koreanTxt []byte

//go:embed NotoSansCJK-SC-Korean.otf
var koreanFont []byte

func main() {
	fmt.Println("========================================")
	fmt.Println("  Turing Complete 한국어 패치 설치")
	fmt.Println("  버전: 0.1059 Beta")
	fmt.Println("========================================")
	fmt.Println()

	gameDir, err := findGameDir()
	if err != nil {
		fmt.Println("[!] 게임 경로를 자동으로 찾지 못했습니다.")
		fmt.Print("    게임 폴더 경로를 직접 입력하세요: ")
		var input string
		fmt.Scanln(&input)
		gameDir = strings.TrimSpace(input)
	}

	if _, err := os.Stat(filepath.Join(gameDir, "translations", "English.txt")); err != nil {
		fmt.Printf("[오류] 올바른 게임 폴더가 아닙니다: %s\n", gameDir)
		waitAndExit(1)
	}

	fmt.Printf("[✓] 게임 경로: %s\n\n", gameDir)

	// 1. 번역 파일 설치
	transPath := filepath.Join(gameDir, "translations", "Korean.txt")
	if err := os.WriteFile(transPath, koreanTxt, 0644); err != nil {
		fmt.Printf("[오류] Korean.txt 설치 실패: %v\n", err)
		waitAndExit(1)
	}
	fmt.Println("[✓] Korean.txt 설치 완료")
	fmt.Println()

	// 2. PCK 폰트 패치
	pckPath := filepath.Join(gameDir, "Turing Complete.pck")
	if _, err := os.Stat(pckPath); err != nil {
		fmt.Println("[!] PCK 파일을 찾을 수 없습니다. 폰트/언어 패치를 건너뜁니다.")
		printDone()
		return
	}

	fmt.Println("[*] PCK 폰트 패치 중 (한글 렌더링 지원 추가)...")
	if err := patchFont(pckPath); err != nil {
		fmt.Printf("[!] 폰트 패치 실패: %v\n", err)
	}

	// 3. globals.gdc 패치
	fmt.Println("[*] 언어 선택지 패치 중 (한국어 항목 추가)...")
	if err := patchGlobals(pckPath); err != nil {
		fmt.Printf("[!] globals.gdc 패치 실패: %v\n", err)
	}

	printDone()
}

func findGameDir() (string, error) {
	home, _ := os.UserHomeDir()
	var candidates []string

	switch runtime.GOOS {
	case "windows":
		candidates = []string{
			`C:\Program Files (x86)\Steam\steamapps\common\Turing Complete`,
			`C:\Program Files\Steam\steamapps\common\Turing Complete`,
			filepath.Join(os.Getenv("USERPROFILE"), `AppData\Local\Steam\steamapps\common\Turing Complete`),
		}
	case "darwin":
		candidates = []string{
			filepath.Join(home, "Library/Application Support/Steam/steamapps/common/Turing Complete"),
		}
	default: // linux
		candidates = []string{
			filepath.Join(home, ".local/share/Steam/steamapps/common/Turing Complete"),
			filepath.Join(home, ".steam/steam/steamapps/common/Turing Complete"),
		}
	}

	for _, c := range candidates {
		if _, err := os.Stat(filepath.Join(c, "translations", "English.txt")); err == nil {
			return c, nil
		}
	}
	return "", fmt.Errorf("not found")
}

// PCK 파일 테이블에서 특정 경로의 엔트리 위치를 반환
// returns: tablePos (offset/size 필드의 시작 위치), error
func findPCKEntry(data []byte, targetPath string) (int, error) {
	const headerSize = 4 + 4 + 4 + 4 + 4 + 64
	if len(data) < headerSize+4 {
		return 0, fmt.Errorf("PCK 파일이 너무 작습니다")
	}

	fileCount := int(binary.LittleEndian.Uint32(data[headerSize:]))
	offset := headerSize + 4

	for i := 0; i < fileCount; i++ {
		if offset+4 > len(data) {
			break
		}
		plen := int(binary.LittleEndian.Uint32(data[offset:]))
		offset += 4
		if offset+plen > len(data) {
			break
		}
		path := strings.TrimRight(string(data[offset:offset+plen]), "\x00")
		offset += plen
		if path == targetPath {
			return offset, nil
		}
		offset += 32 // offset(8) + size(8) + md5(16)
	}
	return 0, fmt.Errorf("엔트리 없음: %s", targetPath)
}

func patchFont(pckPath string) error {
	data, err := os.ReadFile(pckPath)
	if err != nil {
		return err
	}
	buf := append([]byte(nil), data...)

	tblPos, err := findPCKEntry(buf, "res://fonts/NotoSansSC-Regular.otf")
	if err != nil {
		return fmt.Errorf("NotoSansSC 엔트리를 찾지 못했습니다 (게임 버전이 다를 수 있음)")
	}

	curSize := binary.LittleEndian.Uint64(buf[tblPos+8:])
	if curSize == uint64(len(koreanFont)) {
		fmt.Println("[✓] PCK 폰트 이미 패치됨")
		return nil
	}

	newOffset := uint64(len(buf))
	buf = append(buf, koreanFont...)
	binary.LittleEndian.PutUint64(buf[tblPos:], newOffset)
	binary.LittleEndian.PutUint64(buf[tblPos+8:], uint64(len(koreanFont)))

	if err := os.WriteFile(pckPath, buf, 0644); err != nil {
		return err
	}
	fmt.Println("[✓] PCK 폰트 패치 완료")
	return nil
}

func patchGlobals(pckPath string) error {
	data, err := os.ReadFile(pckPath)
	if err != nil {
		return err
	}
	buf := append([]byte(nil), data...)

	tblPos, err := findPCKEntry(buf, "res://main_scripts/globals.gdc")
	if err != nil {
		return fmt.Errorf("globals.gdc 엔트리를 찾지 못했습니다 (게임 버전이 다를 수 있음)")
	}

	gdcOffset := binary.LittleEndian.Uint64(buf[tblPos:])
	gdcSize := binary.LittleEndian.Uint64(buf[tblPos+8:])
	gdc := append([]byte(nil), buf[gdcOffset:gdcOffset+gdcSize]...)

	francais := []byte("Français")
	hangugeo := []byte("한국어")
	french := []byte("French")
	korean := []byte("Korean")

	if bytes.Contains(gdc, hangugeo) {
		fmt.Println("[✓] globals.gdc 이미 패치됨 (한국어 선택지 존재)")
		return nil
	}

	posFr := bytes.Index(gdc, francais)
	posEn := bytes.Index(gdc, french)
	if posFr == -1 || posEn == -1 {
		return fmt.Errorf("Français/French 문자열 없음 (게임 버전이 다를 수 있음)")
	}

	copy(gdc[posFr:], hangugeo)
	copy(gdc[posEn:], korean)

	newOffset := uint64(len(buf))
	buf = append(buf, gdc...)
	binary.LittleEndian.PutUint64(buf[tblPos:], newOffset)
	binary.LittleEndian.PutUint64(buf[tblPos+8:], uint64(len(gdc)))

	if err := os.WriteFile(pckPath, buf, 0644); err != nil {
		return err
	}
	fmt.Println("[✓] globals.gdc 패치 완료 - '한국어' 선택지 추가됨")
	return nil
}

func printDone() {
	fmt.Println()
	fmt.Println("==========================================")
	fmt.Println("  설치 완료!")
	fmt.Println()
	fmt.Println("  게임 실행 후:")
	fmt.Println("  Options > Language > 한국어 선택")
	fmt.Println("  → 한국어로 표시됩니다")
	fmt.Println("==========================================")
	waitAndExit(0)
}

func waitAndExit(code int) {
	if runtime.GOOS == "windows" {
		fmt.Println("\n아무 키나 누르면 종료됩니다...")
		fmt.Scanln()
	}
	os.Exit(code)
}
