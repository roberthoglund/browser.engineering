import logging


class URL:
    def __init__(self, url: str, version: str):
        self.version = version
        self.view_source = False
        if url.startswith("view-source:"):
            _, url = url.split(":", 1)
            self.view_source = True
        if url.startswith("data:"):
            self.scheme, url = url.split(":", 1)
        else:
            self.scheme, url = url.split("://", 1)
            assert self.scheme in ["http", "https", "file"]

        if self.scheme == "file":
            self.path = url
        elif self.scheme == "data":
            self.data_mime_type, self.data_content = url.split(",", 1)
        else:
            if self.scheme == "http":
                self.port = 80
            else:
                self.port = 443

            if "/" not in url:
                url += "/"

            self.host, url = url.split("/", 1)
            if ":" in self.host:
                self.host, port = self.host.split(":", 1)
                self.port = int(port)

            self.path = "/" + url

    def __str__(self):
        return f"{self.scheme}://{self.host}{self.path}"

    def resolve(self, url):
        if "://" in url:
            return URL(url, self.version)
        if not url.startswith("/"):
            dir, _ = self.path.rsplit("/", 1)
            while url.startswith("../"):
                _, url = url.split("/", 1)
                if "/" in dir:
                    dir, _ = dir.rsplit("/", 1)
            url = dir + "/" + url
        if url.startswith("//"):
            return URL(f"{self.scheme}:{url}", self.version)
        else:
            return URL(f"{self.scheme}://{self.host}{url}", self.version)

    def request(self, headers=None) -> str:
        if self.scheme == "file":
            return self._file_request()
        elif self.scheme == "data":
            return self.data_content
        else:
            return self._socket_request(headers)

    def _file_request(self) -> str:
        with open(self.path, "r") as f:
            return f.read()

    def _socket_request(self, headers=None) -> str:
        import socket

        request_headers = {
            "Host": self.host,
            "Connection": "close",
            "User-Agent": f"browser.engineering/{self.version}",
        }

        if headers:
            request_headers.update(headers)

        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )

        s.connect((self.host, self.port))
        if self.scheme == "https":
            import ssl

            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)

        request = f"GET {self.path} HTTP/1.1\r\n"
        for header, value in request_headers.items():
            request += f"{header}: {value}\r\n"
        request += "\r\n"

        logging.debug(f"URL request:\n{request}")

        s.send(request.encode("utf8"))

        response = s.makefile("r", encoding="utf8", newline="\r\n")
        _status_line = response.readline()
        # version, status, explanation = status_line.split(" ", 2)

        response_headers = {}
        while True:
            line = response.readline()
            if line in ("\n", "\r\n"):
                break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()

        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers

        content = response.read()
        s.close()
        return content
