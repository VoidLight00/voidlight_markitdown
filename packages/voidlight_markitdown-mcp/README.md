# VoidLight-MarkItDown-MCP

[![PyPI](https://img.shields.io/pypi/v/voidlight-markitdown-mcp.svg)](https://pypi.org/project/voidlight-markitdown-mcp/)
![PyPI - Downloads](https://img.shields.io/pypi/dd/voidlight-markitdown-mcp)
[![Built by VoidLight](https://img.shields.io/badge/Built%20by-VoidLight-blue)](https://github.com/voidlight/voidlight_markitdown)

The `voidlight-markitdown-mcp` package provides a lightweight STDIO, Streamable HTTP, and SSE MCP server for calling VoidLight MarkItDown with enhanced Korean language support.

`voidlight-markitdown-mcp` 패키지는 한국어 지원이 강화된 VoidLight MarkItDown을 호출하기 위한 경량 STDIO, Streamable HTTP, SSE MCP 서버를 제공합니다.

## Features / 기능

- **Enhanced Korean Support / 강화된 한국어 지원**
  - Korean text normalization / 한국어 텍스트 정규화
  - Improved encoding handling for Korean documents / 한국어 문서의 인코딩 처리 개선
  - Better support for mixed Korean-Chinese texts / 한자 혼용 텍스트 지원 향상
  - Optimized Korean PDF/DOCX conversion / 한국어 PDF/DOCX 변환 최적화

## Tools / 도구

It exposes two tools / 두 가지 도구를 제공합니다:

1. `convert_to_markdown(uri)` - Standard conversion for any URI / 모든 URI에 대한 표준 변환
2. `convert_korean_document(uri, normalize_korean)` - Korean-optimized conversion / 한국어 최적화 변환

Where URI can be any `http:`, `https:`, `file:`, or `data:` URI.

## Installation / 설치

To install the package, use pip / pip를 사용하여 패키지를 설치합니다:

```bash
pip install voidlight-markitdown-mcp
```

## Usage / 사용법

To run the MCP server using STDIO (default) / STDIO를 사용하여 MCP 서버 실행 (기본값):

```bash	
voidlight-markitdown-mcp
```

To run the MCP server using Streamable HTTP and SSE / Streamable HTTP와 SSE를 사용하여 MCP 서버 실행:

```bash	
voidlight-markitdown-mcp --http --host 127.0.0.1 --port 3001
```

## Running in Docker / Docker에서 실행

To run `voidlight-markitdown-mcp` in Docker, build the Docker image using the provided Dockerfile:
Docker에서 실행하려면 제공된 Dockerfile을 사용하여 Docker 이미지를 빌드합니다:

```bash
docker build -t voidlight-markitdown-mcp:latest .
```

And run it using / 다음 명령으로 실행:

```bash
docker run -it --rm voidlight-markitdown-mcp:latest
```

This will be sufficient for remote URIs. To access local files, you need to mount the local directory into the container:
원격 URI에는 이것으로 충분합니다. 로컬 파일에 액세스하려면 로컬 디렉토리를 컨테이너에 마운트해야 합니다:

```bash
docker run -it --rm -v /home/user/data:/workdir voidlight-markitdown-mcp:latest
```

## Accessing from Claude Desktop / Claude Desktop에서 액세스

It is recommended to use the Docker image when running the MCP server for Claude Desktop.
Claude Desktop용 MCP 서버를 실행할 때는 Docker 이미지를 사용하는 것이 좋습니다.

Follow [these instructions](https://modelcontextprotocol.io/quickstart/user#for-claude-desktop-users) to access Claude's `claude_desktop_config.json` file.

Edit it to include the following JSON entry / 다음 JSON 항목을 포함하도록 편집합니다:

```json
{
  "mcpServers": {
    "voidlight_markitdown": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "voidlight-markitdown-mcp:latest"
      ]
    }
  }
}
```

If you want to mount a directory / 디렉토리를 마운트하려면:

```json
{
  "mcpServers": {
    "voidlight_markitdown": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-v",
        "/home/user/data:/workdir",
        "voidlight-markitdown-mcp:latest"
      ]
    }
  }
}
```

## Korean Document Examples / 한국어 문서 예제

```python
# Standard conversion / 표준 변환
result = await convert_to_markdown("file:///path/to/korean_document.pdf")

# Korean-optimized conversion / 한국어 최적화 변환
result = await convert_korean_document(
    "file:///path/to/korean_document.docx",
    normalize_korean=True  # 한국어 텍스트 정규화 활성화
)
```

## Debugging / 디버깅

To debug the MCP server you can use the `mcpinspector` tool.
MCP 서버를 디버그하려면 `mcpinspector` 도구를 사용할 수 있습니다.

```bash
npx @modelcontextprotocol/inspector
```

Connect to the inspector through the specified host and port (e.g., `http://localhost:5173/`).

### Connection Options / 연결 옵션

If using STDIO:
* select `STDIO` as the transport type
* input `voidlight-markitdown-mcp` as the command
* click `Connect`

If using Streamable HTTP:
* select `Streamable HTTP` as the transport type
* input `http://127.0.0.1:3001/mcp` as the URL
* click `Connect`

If using SSE:
* select `SSE` as the transport type
* input `http://127.0.0.1:3001/sse` as the URL
* click `Connect`

Finally:
* click the `Tools` tab
* click `List Tools`
* click `convert_to_markdown` or `convert_korean_document`
* run the tool on any valid URI

## HTTP/SSE Client Requirements / HTTP/SSE 클라이언트 요구사항

When using HTTP or SSE mode, clients must send the proper Accept header:
HTTP 또는 SSE 모드를 사용할 때 클라이언트는 올바른 Accept 헤더를 보내야 합니다:

```python
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json, text/event-stream'  # Required for Streamable HTTP!
}

# Send all requests to the /mcp endpoint
response = requests.post('http://localhost:3001/mcp', json=request, headers=headers)
```

Without the proper Accept header, you will receive a `406 Not Acceptable` error.
올바른 Accept 헤더가 없으면 `406 Not Acceptable` 오류가 발생합니다.

## Environment Variables / 환경 변수

- `VOIDLIGHT_MARKITDOWN_ENABLE_PLUGINS` - Enable/disable plugins (default: "false") / 플러그인 활성화/비활성화 (기본값: "false")

## Security Considerations / 보안 고려사항

The server does not support authentication, and runs with the privileges of the user running it. For this reason, when running in SSE or Streamable HTTP mode, it is recommended to run the server bound to `localhost` (default).

서버는 인증을 지원하지 않으며 실행하는 사용자의 권한으로 실행됩니다. 이러한 이유로 SSE 또는 Streamable HTTP 모드에서 실행할 때는 서버를 `localhost`(기본값)에 바인딩하여 실행하는 것이 좋습니다.

## License / 라이선스

This project is licensed under the MIT License - see the LICENSE file for details.
이 프로젝트는 MIT 라이선스에 따라 라이선스가 부여됩니다 - 자세한 내용은 LICENSE 파일을 참조하세요.