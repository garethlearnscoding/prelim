from pathlib import Path
import re
import csv
import sys

class CONFIG:
    sub_paths = {
        "2PH":Path("manual/Physics"),
        "2EC":Path("manual/Econs"),
        "1GP":Path("manual/gp")
    }
    T_SCHOOL = ["RI","NJC","HCI","YIJC","CJC","NYJC","RVHS","JPJC","ASRJC","ACJC","DHS","EJC","TMJC","TJC","VJC","SAJC","MI"]
    T_PAPERS = {
            "INSERT":"2",
            "EQ":"2",
            "ESSAY": "2",
            "CSQ":"1",
            "PAPER 1":"1",
            "PAPER 2":"2",
            "PAPER 3":"3",
            "PAPER 4":"4",
            "1":"1",
            "2":"2",
            "3":"3",
            "4":"4",
            "P1":"1",
            "P2":"2",
            "P3":"3",
            "01":"1",
            "02":"2",
            "03":"3",
            "04":"4",
            "P4":"4"
        }
    T_QUESTION = ["QP","Que","CSQ","book"] + ["Q"+str(i) for i in range(8)]
    T_SOL = {"MS", "ANS", "SOL", "SCHEME", "GUIDE", "SS", "SUGG","SAMS","REPORT","SAS"}
    T_MISC = ["insert"]
    SCHOOL_PAT = re.compile("(" + "|".join(map(re.escape, T_SCHOOL)) + ")",re.IGNORECASE)
    PAPER_PAT = re.compile(r"(" + "|".join(map(re.escape, sorted(T_PAPERS.keys(),reverse=True))) + r")",re.IGNORECASE)
    QUE_PAT = re.compile(r"(" + "|".join(map(re.escape, T_QUESTION)) + r")",re.IGNORECASE)
    SOL_PAT = re.compile(r"(" + "|".join(map(re.escape, T_SOL)) + r")",re.IGNORECASE)
    MISC_PAT = re.compile(r"(" + "|".join(map(re.escape, T_MISC)) + r")",re.IGNORECASE)
    T_QNO = ["CSQ","Q","EQ"]
    T_QT = ["AQ"]
    QNO_PAT = re.compile(rf"(({'|'.join(map(re.escape, T_QNO))})\d{{1,2}}[A-Za-z]*|{'|'.join(map(re.escape,T_QT))})",re.IGNORECASE)

    def __init__(self,subject_code):
        Path("store.csv").touch(exist_ok=True)
        Path("skip.csv").touch(exist_ok=True)
        Path("ltr.csv").touch(exist_ok=True)
        self.folder = CONFIG.sub_paths[subject_code]
        self.code = subject_code

    @classmethod
    def env_cfg(cls,subject_code):
        if subject_code not in CONFIG.sub_paths:
            return False
        else:
            return cls(subject_code)
        

    @staticmethod
    def prog():
        with open("store.csv") as f:
            SKIPPED = [i[0] for i in csv.reader(f)]
    
        with open("skip.csv") as f:
            READ = [i[0] for i in csv.reader(f)]

        with open("ltr.csv") as f:
            LTR = [i[0] for i in csv.reader(f)]

        return SKIPPED + READ + LTR



class File:
    def __init__(self,pdf,school=None,year=None,p_no=None,doc=None):
        self.pdf = pdf
        self.school = school
        self.year = year
        self.p_no = p_no
        self.doc = doc
        self._str = None
        if pdf is not None:
            self.year = pdf.parent.stem
            str_to_match = pdf.stem
            for i in ["lims","j2","h2","jc2","h1"] + [self.pdf.parent.stem]:
                str_to_match = str_to_match.lower().replace(i,"")
            for i in ["answer book","ans book"]:
                str_to_match = str_to_match.replace("answer booklet","book")
            self._str = str_to_match

    def __repr__(self):
        return f"<File {self.as_row()}>"

    def as_row(self):
        return [str(self.pdf), self.school, self.year, self.p_no, self.doc]
    
    @classmethod
    def from_row(cls,row):
        row[0] = Path(row[0])
        return cls(*row)

    def rename(self,env):
        folder_path = self.pdf.parent / f"{env.code}_PRELIM_{self.year}_{self.school}"
        if self.p_no != "":
            self.p_no = "0"+self.p_no
        file_path = folder_path / f"{env.code}_PRELIM_{self.year}_{self.school}_{self.p_no}{self.doc}.pdf"
        folder_path.mkdir(parents=True, exist_ok=True)
        if not file_path.exists():
            self.pdf.rename(file_path)
            print(f"{self.pdf} -> {file_path}")
            return
        print(f"SKIPPED: {self.pdf}")

        

    @staticmethod
    def presence(_str,pattern,label,value_map=None):
        m = pattern.search(_str)
        if m:
            found = m.group(1).upper()
            print("Found:",found)
            term = value_map[found] if value_map else found
            proceed = input(f"{term} | Enter / Other {label}: ")
            if proceed == "":
                return value_map[found] if value_map else found
            elif proceed == " ":
                return ""
            else:
                return proceed
        else:
            return None

    def handle_schl(self,state):
        self.school = File.presence(self._str, CONFIG.SCHOOL_PAT, "School")
        if self.school is None:
            term = input(f"{state.school} | School: ")
            if term == "":
                self.school = state.school
            else:
                self.school = term

    def handle_pno(self,state):
        self.p_no = File.presence(self._str, CONFIG.PAPER_PAT, "Paper No", CONFIG.T_PAPERS)
        if self.p_no is None:
            term = input(f"{state.p_no} | Paper No: ")
            if term == "":
                self.p_no = state.p_no
            elif term == " ":
                self.p_no = ""
            else:
                self.p_no = term

    def handle_doc(self):
        qno = CONFIG.QNO_PAT.search(self._str)
        que = CONFIG.QUE_PAT.search(self._str)
        sol = CONFIG.SOL_PAT.search(self._str)
        misc = CONFIG.MISC_PAT.search(self._str)
        if que is not None and "book"in que.groups():
            sol = False
        if que and misc:
            msg = f"Found: {que.group(1)} | {misc.group(1)}"
            term = "QP_I"
        elif sol and que:
            msg = f"Found: {que.group(1)} | {sol.group(1)}"
            term = "QP_A"
        elif misc:
            msg = f"Found: {misc.group(1)}"
            term = "I"
        elif que:
            msg = f"Found: {que.group(1)}"
            term = "QP"
        elif sol:
            msg = f"Found: {sol.group(1)}"
            term = "A"
        else:
            term = False
        if term:
            print(msg)
            proceed = input(f"{term} | Enter / Other Doc: ")
            if proceed == "":
                self.doc = term
            else:
                self.doc = proceed
        else:
            prev = "QP"
            term = input(f"{prev} | Doc: ")
            if term == "":
                self.doc = prev
            else:
                self.doc = term
        if qno:
            term = qno.group(1).upper()
            print(f"Found: {term}")
            proceed = input(f"{term} | Enter / Other Q NO")
            if proceed == "":
                q_no = term
            else: 
                q_no = proceed
            self.doc = q_no.upper() + "_" + self.doc

        

    def store(self):
        with open("store.csv","a",newline="\n") as f:
            writer = csv.writer(f)
            writer.writerow(self.as_row())
            

def build_store(env):
    ignore = CONFIG.prog()
    state = File(None)
    for folder in sorted(env.folder.iterdir()):
        if folder.is_dir():
            for pdf in [pdf for pdf in folder.glob("*.pdf") if str(pdf) not in ignore]:
                do = input("File: "+ pdf.stem)
                if do == " ":
                    with open("skip.csv","a") as f:
                        f.write(f"{pdf}\n")
                    continue
                elif do =="l":
                    with open("ltr.csv",'a') as f:
                        f.write(f"{pdf}\n")
                    continue
                curr = File(pdf)
                curr.handle_schl(state)
                curr.handle_pno(state)
                curr.handle_doc()
                state = curr
                curr.store()
                print("----------------------")
                print()

def rename_files(env):
    with open("store.csv") as f:
        data = [File.from_row(i) for i in list(csv.reader(f))]
    for i in data:
        i.rename(env)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("forgot arguments")
    
    code = sys.argv[-1]
    ENV = CONFIG.env_cfg(code)
    if ENV is False:
        print(f"Unknown subject code: {code}")
        sys.exit(0)

    if sys.argv[-2] == "-s":
        build_store(ENV)
    elif sys.argv[-2] == "-r":
        rename_files(ENV)