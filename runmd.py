import os
import sys


class Parser:
    def __init__(self, file, is_match_inline=True):
        self.file = file
        self.is_match_inline = is_match_inline
        self.line_no = -1
        self.lines = None
        self.current_line = ""
        self.read_file()
        self.code_list = []
        self.match()

    def read_file(self):
        try:
            with open(self.file, "r", encoding="utf8") as f:
                self.lines = f.readlines()
        except FileNotFoundError as e:
            print(e)
            sys.exit(1)

    def match(self):
        self.advance()
        while self.line_no < len(self.lines):
            if self.current_line.startswith("```"):
                self.match_block()
                self.advance()
            elif "`" in self.current_line and self.is_match_inline:
                self.match_inline()
                self.advance()
            else:
                self.advance()

    def match_block(self):
        language = self.current_line.replace("```", "").strip().lower()
        start_line = self.line_no
        code = ""
        while True:
            self.advance()
            if self.current_line.strip() != "```":
                code += self.current_line
            else:
                end_line = self.line_no
                self.code_list.append(Code(len(self.code_list), language, start_line, end_line, "block", code))
                break

    def match_inline(self):
        index_list = []
        for index, value in enumerate(self.current_line):
            if value == "`":
                index_list.append(index)
        for i in range(0, len(index_list), 2):
            index = len(self.code_list)
            line_no = self.line_no
            code = self.current_line[index_list[i] + 1:index_list[i + 1]]
            self.code_list.append(Code(len(self.code_list), None, line_no, line_no, "inline", code))

    def advance(self):
        self.line_no += 1
        if self.line_no < len(self.lines):
            self.current_line = self.lines[self.line_no]

    def reload(self, file=None):
        if file is None:
            self.__init__(self.file)
        else:
            self.__init__(file)


class Code:
    def __init__(self, index, language, start_line, end_line, type_, code_=None):
        self.index = index
        self.language = language
        self.start_line = start_line
        self.end_line = end_line
        self.type = type_
        self.code = code_

    def run(self, language=None):
        try:
            if language is not None:
                self.language = language
            print("current language: " + self.language)
            if self.language == "python":
                exec(self.code)
            elif self.language == "shell":
                os.system(self.code)
            else:
                print("请指定运行语言")

        except Exception as e:
            self.failed_run(e)
        finally:
            return

    def failed_run(self, exception=None):
        print(f"Failed to run the code!\n"
              f"index={self.index}\nlanguage={self.language}\n"
              f"code:\n{self.code}\n"
              f"Exception:{exception if exception is not None else ''}")

    def __repr__(self):
        return str([self.index, self.language, self.start_line, self.end_line, self.type, self.code])


def main():
    try:
        file_path = os.path.normpath(sys.argv[1])
        if not os.path.isfile(file_path):
            print("file not found!")
            sys.exit(1)
    except:
        print("usage: python runmd.py <file_path>")
        sys.exit()

    m = Parser(file_path)
    code = m.code_list
    usage = """usage:
    help h ?: 查看帮助
    show s: 显示所有代码
    run r <index> [language]: 运行指定代码块中的代码
    reload [file]: 重新加载文件，文件名可选
    """
    while True:
        try:
            cmd = input("runmd >  ")
            if cmd == "":
                continue

            arg = list(filter(None, cmd.split(" ")))
            command, args = arg[0].lower(), arg[1:] if len(arg) > 1 else None
            if command == "quit" or command == "q":
                break
            if command == "show" or command == "s":
                for i in code:
                    print(i)
                continue
            if command == "help" or command == "h" or command == "?":
                print(usage)
                continue
            if command == "run" or command == "r":
                if args is None:
                    print("usage: run <index> [language]")
                elif len(args) == 1:
                    code[int(args[0])].run()
                elif len(args) == 2:
                    code[int(args[0])].run(args[1])
                else:
                    print("usage: run <index> [language]")
                continue
            if command.isnumeric():
                if args is None:
                    code[int(command)].run()
                elif len(args) == 1:
                    code[int(command)].run(args[1])
                else:
                    print("usage : <index> [language]")
                continue
            if command == "reload":
                if args is None:
                    m.reload()
                elif len(args) == 1:
                    m.reload(args[0])
                else:
                    print("usage : reload [file]")
                code = m.code_list
                continue
        except KeyboardInterrupt:
            if input("exit?  (y/n)[n]").lower() == "y":
                sys.exit(0)


if __name__ == '__main__':
    main()
