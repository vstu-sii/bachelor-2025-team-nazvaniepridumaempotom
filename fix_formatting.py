# scripts/fix_formatting.py
import os


def fix_black_issues():
    """Fix Black formatting issues."""

    # Список проблемных файлов из ошибки
    problematic_files = [
        "backend/schemas/user.py",
        # Добавьте другие файлы здесь
    ]

    for file_path in problematic_files:
        if os.path.exists(file_path):
            print(f"Fixing {file_path}...")

            # Прочитать содержимое файла
            with open(file_path, "r") as f:
                content = f.read()

            # Исправить распространенные проблемы
            content = content.replace(
                "username: Optional[str] = None", "username: str | None = None"
            )

            # Добавить импорт если нужно
            if "from typing import Optional" in content and "str | None" in content:
                # Удалить ненужный импорт
                lines = content.split("\n")
                lines = [
                    line for line in lines if "from typing import Optional" not in line
                ]
                content = "\n".join(lines)

            # Записать обратно
            with open(file_path, "w") as f:
                f.write(content)

    print("Formatting fixed!")


if __name__ == "__main__":
    fix_black_issues()
