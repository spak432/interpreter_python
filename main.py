from enum import Enum

class Tokentype (Enum):
	INTEGER = 'INTEGER'
	PLUS = 'PLUS'
	MINUS = 'MINUS'
	MUL = 'MUL'
	DIV = 'DIV'
	EOF = 'EOF'
	LPAREN = 'LPAREN'
	RPAREN = 'RPAREN'

class Token ():
	def __init__ (self, type, value):
		self.type = type
		self.value = value
	
	def __str__ (self):
		return f'Token({self.type}, {self.value})'
	
	def __repr__ (self):
		return self.__str__()

# AST

class AST ():
    pass

class BinOp (AST):
	def __init__ (self, left, op, right):
		self.left = left
		self.op = self.token = op
		self.right = right

class UnaryOp (AST):
	def __init__ (self, op, right):
		self.op = self.token = op
		self.right = right
		
class Num (AST):
    def __init__ (self, token):
        self.token = token
        self.value = token.value

# Lexer

class Lexer ():
	def __init__ (self, text):
		self.text = text
		self.pos = 0
		self.current_char = self.text[self.pos]
	
	def error (self):
		raise Exception ("Invalid character")
	
	def advance (self):
		self.pos += 1
		if self.pos > len (self.text) -1:
			self.current_char = None
		else:
			self.current_char = self.text[self.pos]

	def skip_whitespace (self):
		while self.current_char is not None and self.current_char.isspace():
			self.advance()

	def integer (self):
		result = ''
		while self.current_char is not None and self.current_char.isdigit():
			result += self.current_char
			self.advance()
		return int (result)

	def get_next_token (self):
		while self.current_char is not None:
			if self.current_char.isspace():
				self.skip_whitespace()
				continue
			if self.current_char.isdigit():
				return Token (Tokentype.INTEGER, self.integer())
			
			if self.current_char == '+':
				self.advance()
				return Token (Tokentype.PLUS, '+')
			
			if self.current_char == '-':
				self.advance()
				return Token (Tokentype.MINUS, '-')
			
			if self.current_char == '*':
				self.advance()
				return Token (Tokentype.MUL, '*')
			
			if self.current_char == '/':
				self.advance()
				return Token (Tokentype.DIV, '/')
			
			if self.current_char == '(':
				self.advance()
				return Token (Tokentype.LPAREN, '(')
			
			if self.current_char == ')':
				self.advance()
				return Token (Tokentype.RPAREN, ')')
			
			self.error()
		
		return Token (Tokentype.EOF, None)

# Parser

class Parser ():
	def __init__ (self, lexer):
		self.lexer = lexer
		self.current_token = self.lexer.get_next_token()
	
	def error (self):
		raise Exception ("Invalid syntax")
	
	def eat (self, token_type):
		if self.current_token.type == token_type:
			self.current_token = self.lexer.get_next_token()
		else:
			self.error()

	def factor (self):
		token = self.current_token
		if token.type in (Tokentype.PLUS, Tokentype.MINUS):
			if token.type == Tokentype.PLUS:
				self.eat (Tokentype.PLUS)
			else:
				self.eat (Tokentype.MINUS)
			node = UnaryOp (token, self.factor())
			return node
		
		elif token.type == Tokentype.INTEGER:
			self.eat (Tokentype.INTEGER)
			return Num (token)
		elif token.type == Tokentype.LPAREN:
			self.eat (Tokentype.LPAREN)
			node = self.expr()
			self.eat (Tokentype.RPAREN)
			return node
	
	def term (self):
		node = self.factor ()
		while self.current_token.type in (Tokentype.MUL, Tokentype.DIV):
			token = self.current_token
			if self.current_token.type == Tokentype.MUL:
				self.eat (Tokentype.MUL)
			elif self.current_token.type == Tokentype.DIV:
				self.eat (Tokentype.DIV)
			node = BinOp (left = node, op=token, right = self.factor())
		return node

	def expr (self):
		node = self.term()
		while self.current_token.type in (Tokentype.PLUS, Tokentype.MINUS):
			token = self.current_token
			if self.current_token.type == Tokentype.PLUS:
				self.eat (Tokentype.PLUS)
			elif self.current_token.type == Tokentype.MINUS:
				self.eat (Tokentype.MINUS)
			node = BinOp (left = node, op = token, right = self.term())
		return node

	def parse (self):
		return self.expr()

# Interpreter

class NodeVisitor ():
	def visit (self, node):
		method_name = 'visit_' + type(node).__name__
		visitor = getattr (self, method_name, self.generic_visit)
		return visitor (node)

	def generic_visit (self, node):
		raise Exception (f"No visit_ {type(node.__name__)} method")
	
class Interpreter (NodeVisitor):
	def __init__ (self, parser):
		self.parser = parser
	
	def visit_BinOp (self, node):
		if node.op.type == Tokentype.PLUS:
			return self.visit (node.left) + self.visit(node.right)
		elif node.op.type == Tokentype.MINUS:
			return self.visit (node.left) - self.visit(node.right)
		elif node.op.type == Tokentype.MUL:
			return self.visit (node.left) * self.visit(node.right)
		elif node.op.type == Tokentype.DIV:
			return self.visit (node.left) / self.visit(node.right)
	
	def visit_UnaryOp (self, node):
		if node.op.type == Tokentype.PLUS:
			return self.visit(node.right)
		elif node.op.type == Tokentype.MINUS:
			return -self.visit(node.right)

	def visit_Num (self, node):
		return node.value

	def interpret (self):
		tree = self.parser.parse()
		return self.visit (tree)

def main ():
	while True:
		try:
			text = input ('>>> ')
		except EOFError:
			break
		if not text:
			continue
		lexer = Lexer (text)
		parser = Parser (lexer)
		interpreter = Interpreter (parser)
		result = interpreter.interpret ()
		
		print (result)

if __name__ == "__main__":
	main ()