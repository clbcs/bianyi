from Lexer import Lexer
from MyParser import MyParser

code = """
    program main;
    var int x;
    var float res_D;
    arr int y[15];
    arr float z[12, 5];
    procedure int A(var int param);
        procedure int B(var int param);
            var float num;
            procedure int C(var int param, arr int a);
            var int x;
            begin
                x := param-1;
                return x;
            end
        begin
            x:= param-1;
            return x;
        end
        procedure float D(var int param);
        var int res_B;
        begin
            x:= param-1;
            res_B := call B(x);
            return res_B;
        end
    begin
        x := param-1;
        res_D := call D(x);
        return res_D;
    end

    begin
        x := 5;
        res_A := call A(x);
        write(x);
    end
"""

lexer = Lexer(code)
tokens = lexer.lex()
parser = MyParser(tokens)
parser.parse()
print(parser.tables)

