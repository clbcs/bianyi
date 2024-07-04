class SymbolTableDict:#符号表的集合,每个符号表对应一个程序块（如函数或过程）
    def __init__(self):
        self.symbol_tables = {} #存储符号表

    def add_table(self, table_name):#添加一个新的符号表
        if table_name in self.symbol_tables:#如果符号表已经存在，抛出 RedefinitionError
            raise RedefinitionError(table_name, 'table_dict')
        self.symbol_tables[table_name] = SymbolTable(table_name)

    def get_table(self, table_name):#获取指定名称的符号表
        if table_name not in self.symbol_tables:#如果符号表不存在，抛出 NotFoundError
            raise NotFoundError(table_name, 'table_dict')
        return self.symbol_tables[table_name]

    def __str__(self):#返回所有符号表的字符串表示形式
        return "\n".join(f"{name}_table:"+ '\n{' + f"{str(table)}" + '\n}' for name, table in self.symbol_tables.items())

class SymbolTable:#一个符号表，包含特定程序块的符号信息
    def __init__(self, table_name):
        self.table_name = table_name
        self.symbol_table = {'name':table_name, 'outer': None,  'argc': None, 'arglist': None, 'code':f'{table_name}_code'}

    def add_symbol(self, name, type, **kwargs):#添加一个新的符号
        if name in self.symbol_table:
            raise RedefinitionError(name, 'symbol_table')
        self.symbol_table[name] = {'type': type, **kwargs}

    def set_attribute(self, name, attribute, value):#设置指定符号的属性
        if name not in self.symbol_table:
            raise NotFoundError(name, 'symbol_table')
        self.symbol_table[name][attribute] = value

    def get_symbol(self, name):#获取指定符号的信息
        if name not in self.symbol_table:
            raise NotFoundError(name, 'table_dict')
        return self.symbol_table.get(name)
    
    def __str__(self):#返回符号表的字符串表示形式
        symbol_info = "\n".join(f"{name}: {info}" for name, info in self.symbol_table.items())
        return f"\n{symbol_info}"
    
class RedefinitionError(Exception):#当符号或符号表已经存在时抛出
    def __init__(self, name, type):
        self.name = name
        self.type = type
        super().__init__(f"'{name}' has already been defined in {type}")

class NotFoundError(Exception):#当符号或符号表不存在时抛出
    def __init__(self, name, type):
        self.name = name
        super().__init__(f"'{name}' is not found in {type}")
    
if __name__ == '__main__':
    # 创建 SymbolTableDict 实例
    symbol_dict = SymbolTableDict()

    # 添加新表
    symbol_dict.add_table('main')

    # 向 'main' 表中添加符号
   # symbol_dict.get_table('main').add_symbol('int', 'x', value=5)
    #symbol_dict.get_table('main').add_symbol('float', 'y', value=3.14)

    # 打印符号表
    print(symbol_dict)
