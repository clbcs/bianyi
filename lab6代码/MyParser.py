from SymbolTable import SymbolTableDict

class MyParser:
    """
    语法分析器识别文法：
    <prog> → program <id>; <block>
    <block> → [<vardecl>][<array>][<proc>]<body>
    <vardecl> → var [<intvar>|<floatvar>];
    <intvar> → int <id>
    <floatvar> → float <id>
    <array> → arr [<intarr>|<floatarr>];
    <intarr> → int <id>[<integer>{,<integer>}]
    <floatarr> → float <id>[<integer>{,<integer>}]
    <proc> → procedure [int|float] <id>([<vardecl>{,<vardecl>}][<arrptt>{,<arrptt>}]);<block>{;<proc>}
    <arrptt> → arr [<intvar>|<floatvar>];
    <body> → begin <statement>{;<statement>}end
    <statement> → <id>{[<integer>{,<integer>}]} := [<exp> | call <id>([<exp>{,<exp>}])] 
                |if <lexp> then <statement>[else <statement>]
                |while <lexp> do <statement>
                |<body>
                |read (<id>{,<id>})
                |write (<exp>{,<exp>})
                |return [<id>|<exp>]
    <lexp> → <exp> <lop> <exp>|odd <exp>
    <exp> → [+|-]<term>{<aop><term>}
    <term> → <factor>{<mop><factor>}
    <factor>→<id>|<integer>|(<exp>)
    <lop> → =|<>|<|<=|>|>=
    <aop> → +|-
    <mop> → *|/
    <id> → l{l|d} (注:l 表示字母)
    <integer> → d{d}
    """
    def __init__(self, tokens):
        self.tokens = iter(tokens)
        self.current_token = None
        #初始化一个符号表对象，用于存储程序中定义的变量、数组、过程等的符号信息
        self.tables = SymbolTableDict()
        self.next_token()
        #该变量用于标记当前是否在解析数组参数类型（arrptt）
        self.is_ptt = False
        #初始化一个空的符号表栈，用于管理嵌套的符号表。在进入新作用域（如过程或嵌套块）时，会将当前符号表推入栈中。
        self.table_stack = []
        self.size = 0
        #用于管理嵌套作用域的偏移量。在进入新作用域时，会将当前偏移量推入栈中。
        self.size_stack = []

    #从迭代器中获取下一个 token 并更新当前 token
    def next_token(self):
        try:
            self.current = next(self.tokens)
            self.current_token = self.current[0]
        #如果没有更多的 token 可供获取，捕获 StopIteration 异常
        except StopIteration:
            self.current_token = None

    #检查当前 token 是否与预期 token 匹配，并在匹配时获取下一个 token。如果不匹配，则抛出语法错误
    def match(self, expected_token):
        if self.current_token == expected_token:
            #如果当前 token 是标识符 <id>
            if self.current_token == "<id>":
                #获取标识符的具体值并存储在 self.current_id 中
                self.current_id = self.current[1]
            self.next_token()
        else:
            raise SyntaxError(f"Expect '{expected_token}' but got '{self.current_token}'.")

    def program(self):
        self.match("program")
        self.tables.add_table(self.current[1])
        self.table_stack.append(self.tables.get_table(self.current[1]))
        self.current_table = self.table_stack[-1]
        self.match("<id>")
        self.match(";")
        self.block()

    def block(self):
        while self.current_token == "var":
            self.vardecl()
        while self.current_token == "arr":
            self.array()
        while self.current_token == "procedure":
            self.proc()
        self.body()

    def vardecl(self):
        self.match("var")
        if self.current_token == "int":
            self.intvar()
        if self.current_token == "float":
            self.floatvar()
        if self.current_token == ";":
            self.match(";")

    def intvar(self):
        self.match("int")
        self.size += 4
        self.current_table.add_symbol(name = self.current[1], type = "int", size = 4)
        self.match("<id>")
    
    def floatvar(self):
        self.match("float")
        self.size += 4
        self.current_table.add_symbol(name = self.current[1], type = "float", size = 4)
        self.match("<id>")

    def array(self):
        self.match("arr")
        if self.current_token == "int":
            self.intarr()
        if self.current_token == "float":
            self.floatarr()
        self.match(";")

    def intarr(self):
        self.match("int")
        arrsize=0
        name = self.current[1]
        self.current_table.add_symbol(name = name, type = "array", size = 0, arrtype = "int")
        self.match("<id>")
        self.match("[")
        size = int(self.current[1])
        self.match("<integer>")
        while self.current_token == ",":
            self.match(",")
            size *= int(self.current[1])
            self.match("<integer>")
        self.match("]")
        arrsize += size * 4 #计算数组大小
        self.size += size * 4
        self.current_table.set_attribute(name = name, attribute = 'size', value = arrsize)
    
    def floatarr(self):
        self.match("float")
        arrsize=0
        name = self.current[1]
        self.current_table.add_symbol(name = name, type = "array", size = 0, arrtype = "float")
        self.match("<id>")
        self.match("[")
        size = int(self.current[1])
        self.match("<integer>")
        while self.current_token == ",":
            self.match(",")
            size *= int(self.current[1])
            self.match("<integer>")
        self.match("]")
        arrsize += size * 4
        self.size += size * 4
        self.current_table.set_attribute(name = name, attribute = 'size', value = arrsize)

    def proc(self):
        self.match("procedure")
        if self.current_token == "int":
            self.match("int")
            rtype = "int"
        if self.current_token == "float":
            self.match("float")
            rtype = "float"
        self.size += 4
        self.current_table.add_symbol(name = self.current[1], type = "proc")
        self.tables.add_table(self.current[1])
        self.table_stack.append(self.tables.get_table(self.current[1]))
        self.size_stack.append(self.size)
        self.size = 0
        self.current_table = self.table_stack[-1]
        name = self.table_stack[-2].symbol_table['name']
        self.current_table.symbol_table['outer'] = f'{name}_table'
        self.current_table.symbol_table['rtype'] = rtype #当前符号表的返回类型
        self.match("<id>")
        arglist = [] #初始化参数列表
        self.match("(")
        while self.current_token != ")": #循环解析参数，直到匹配右括号
            if self.current_token == "var":
                self.vardecl()
                arglist.append(self.current_id)
            if self.current_token == "arr":
                self.arrptt()
                arglist.append(self.current_id)
            if self.current_token == ",":
                self.match(",")
        self.match(")")
        self.match(";")
        self.current_table.symbol_table['argc'] = len(arglist) #参数个数
        self.current_table.symbol_table['arglist'] = tuple(arglist) #参数列表
        self.block() #解析过程体
        if self.current_token == ";":
            self.proc()
    
    def arrptt(self): #解析过程参数列表中的数组指针类型
        self.match("arr")
        if self.current_token == "int":
            self.intvar()
            self.current_table.set_attribute(name = self.current_id, attribute = 'type', value = 'arrptt')
        if self.current_token == "float":
            self.floatvar()
            self.current_table.set_attribute(name = self.current_id, attribute = 'type', value = 'arrptt')
 
    def body(self):
        self.match("begin")
        self.statement()
        self.match(";")
        while self.current_token != "end": #当前 token 不是 "end" 时，继续循环解析语句
            self.statement() #解析一个语句
            self.match(";")
        self.match("end")
        self.table_stack.pop() #弹出符号表栈和尺寸栈，恢复前一个语句块的状态
        if self.table_stack:
            self.current_table = self.table_stack[-1]
        if self.size_stack:
            self.size = self.size_stack[-1]
            self.size_stack.pop()

    def statement(self):
        if self.current_token == "<id>": #赋值语句和函数调用
            self.match("<id>")
            if self.current_token == "[":
                self.match("[")
                self.match("<integer>")
                while self.current_token == ",":
                    self.match(",")
                    self.match("<integer>")
                self.match("]")
            self.match(":=")
            if self.current_token == "call":
                self.match("call")
                self.match("<id>")
                self.match("(")
                if self.current_token != ")":
                    self.exp()
                    while self.current_token == ",":
                        self.match(",")
                        self.exp()
                self.match(")")
            else:
                self.exp()
        elif self.current_token == "if": #条件语句
            self.match("if")
            self.lexp()
            self.match("then")
            self.statement()
            if self.current_token == "else":
                self.match("else")
                self.statement()
        elif self.current_token == "while": #循环语句
            self.match("while")
            self.lexp()
            self.match("do")
            self.statement()
        elif self.current_token == "begin": #复合语句
            self.body()
        elif self.current_token == "read":
            self.match("read")
            self.match("(")
            self.match("<id>")
            while self.current_token == ",": #输入语句
                self.match(",")
                self.match("<id>")
            self.match(")")
        elif self.current_token == "write": #输出语句
            self.match("write")
            self.match("(")
            self.exp()
            while self.current_token == ",":
                self.match(",")
                self.exp()
            self.match(")")
        elif self.current_token == "return": #返回语句
            self.match("return")
            if self.current_token == "<id>":
                self.match("<id>")
            else:
                self.exp()

    def lexp(self):
        if self.current_token == "odd":#奇数检查 (odd <exp>)
            self.match("odd")
            self.exp()
        else:   #一般比较运算 (<exp> <lop> <exp>)
            self.exp()
            self.match("<lop>")
            self.exp()

    def exp(self): #解析和处理表达式
        if self.current_token in ["+", "-"]: #处理一元加减号
            self.match(self.current_token)
        self.term()#调用 term 方法，处理表达式中的项。项可以是一个因子或者因子的乘积或商。
        while self.current_token in ["+", "-"]: #处理二元加减法
            self.match(self.current_token)
            self.term()

    def term(self):
        self.factor() #处理因子
        while self.current_token in ["*", "/"]:#处理乘法和除法运算
            self.match(self.current_token)
            self.factor()

    def factor(self):
        if self.current_token == "<id>": #因子可以是一个标识符
            self.match("<id>")
        elif self.current_token == "<integer>": #一个整数
            self.match("<integer>")
        elif self.current_token == "(": #包含表达式的括号
            self.match("(")
            self.exp()
            self.match(")")
        else:
            raise SyntaxError("Expected identifier, integer, or '('.")

    def parse(self): #启动解析过程
        self.program() #调用 program 方法，启动整个程序的解析过程。program 方法是解析的入口点。
        if self.current_token is not None: #检查是否有多余的 token
            raise SyntaxError("Unexpected tokens after end of program.")
       
