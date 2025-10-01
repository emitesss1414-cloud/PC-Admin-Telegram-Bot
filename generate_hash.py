import bcrypt
import getpass
import argparse


def make_hash_from_password(password: str) -> str:
	pw = password.encode('utf-8')
	return bcrypt.hashpw(pw, bcrypt.gensalt()).decode()


def main():
	parser = argparse.ArgumentParser(description='Generate bcrypt hash for .env')
	parser.add_argument('--password', '-p', help='Plain password to hash (optional). If omitted, will prompt securely.')
	args = parser.parse_args()

	# Support multiple passwords separated by comma
	if args.password:
		raw = args.password
	else:
		# fallback to secure prompt; user may enter multiple passwords comma-separated
		raw = getpass.getpass("Введите пароль(и) для хеширования (через запятую, если несколько): ")

	passwords = [p.strip() for p in raw.split(',') if p.strip()]
	if not passwords:
		print("Нет введённых паролей. Выход.")
		return

	hashes = [make_hash_from_password(pw) for pw in passwords]
	joined = ','.join(hashes)

	# Print an .env-friendly line. The project supports multiple hashes separated by commas.
	print("Скопируйте и вставьте в ваш .env файл следующую строку:")
	print()
	print(f'BOT_PASSWORD_HASHES={joined}')


if __name__ == '__main__':
	main()