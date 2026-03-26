from pathlib import Path


class NoStudentException(Exception):
    """Raised when the requested student does not exist."""


class NoSubjectException(Exception):
    """Raised when the requested subject does not exist for a student."""


class GradeSystem:
    def __init__(self) -> None:
        self.student_grade: dict[str, dict[str, int]] = {}

    def search_grade(self, student_no: str, subject: str) -> int:
        if student_no not in self.student_grade:
            raise NoStudentException("查無此學生")

        student_data = self.student_grade[student_no]
        if subject not in student_data:
            raise NoSubjectException("查無此科目成績")
        return student_data[subject]

    def search_all_grade(self, student_no: str) -> str:
        if student_no not in self.student_grade:
            raise NoStudentException("查無此學生")

        student_data = self.student_grade[student_no]
        return " ".join(f"{subject} {score}" for subject, score in student_data.items())

    def insert_grade(self, data: str) -> None:
        student_data = data.split()
        if len(student_data) < 3 or len(student_data[1:]) % 2 != 0:
            raise ValueError("資料格式錯誤，格式應為: 學號 科目 分數 [科目 分數 ...]")

        student_no = student_data[0]
        subjects = student_data[1:]
        subject_grade: dict[str, int] = {}
        for index in range(0, len(subjects), 2):
            subject = subjects[index]
            try:
                grade = int(subjects[index + 1])
            except ValueError as error:
                raise ValueError(f"科目 {subject} 的分數必須是整數") from error
            subject_grade[subject] = grade

        self.student_grade[student_no] = subject_grade

    def delete_grade(self, student_no: str) -> None:
        if student_no in self.student_grade:
            del self.student_grade[student_no]


class GradeSystemDriver:
    def __init__(self) -> None:
        self.grade_system = GradeSystem()
        self.file_path = str(Path(__file__).with_name("grade2.txt"))

    def load_data(self) -> None:
        if not Path(self.file_path).exists():
            return

        with open(self.file_path, "r", encoding="utf-8") as file:
            for line_no, line in enumerate(file, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    self.grade_system.insert_grade(line)
                except ValueError as error:
                    print(f"略過無效資料 (line {line_no}): {error}")

        print(f"已從 {self.file_path} 載入成績資料")

    def save_data(self) -> None:
        with open(self.file_path, "w", encoding="utf-8") as file:
            for student_no, subject_scores in self.grade_system.student_grade.items():
                data = [student_no]
                for subject, score in subject_scores.items():
                    data.extend([subject, str(score)])
                file.write(" ".join(data) + "\n")

    def run(self) -> None:
        self.load_data()

        while True:
            print("\n成績管理系統")
            print("請選擇操作：")
            print("1. 查詢單一科目成績")
            print("2. 查詢學生全部成績")
            print("3. 新增或覆寫學生成績")
            print("4. 刪除學生成績")
            print("5. 儲存並離開")

            choice = input("請輸入選項：")

            if choice == "1":
                try:
                    student_id_subject = input("請輸入學號與科目 (例如: 97501 DS): ")
                    student_id, subject = student_id_subject.split()
                    grade = self.grade_system.search_grade(student_id, subject)
                    print(f"{student_id} 的 {subject} 成績是 {grade}")
                except ValueError:
                    print("輸入格式錯誤，請使用：學號 科目")
                except (NoSubjectException, NoStudentException) as error:
                    print(error)
            elif choice == "2":
                try:
                    student_id = input("請輸入學號：")
                    all_grades = self.grade_system.search_all_grade(student_id)
                    print(f"{student_id} 的全部成績如下：\n{all_grades}")
                except NoStudentException as error:
                    print(error)
            elif choice == "3":
                student_data = input(
                    "請輸入學號、科目與成績 (例如: 97531 DS 80 DM 80 LA 80): "
                )
                try:
                    self.grade_system.insert_grade(student_data)
                    print("新增完成")
                except ValueError as error:
                    print(error)
            elif choice == "4":
                student_id = input("請輸入學號：")
                self.grade_system.delete_grade(student_id)
                print(f"已刪除學生 {student_id} 的成績資料")
            elif choice == "5":
                print("======= 結束 =======")
                self.save_data()
                break
            else:
                print("無效選項，請重新輸入")


if __name__ == "__main__":
    GradeSystemDriver().run()
