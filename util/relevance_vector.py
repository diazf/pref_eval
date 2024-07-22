import sys
from tracemalloc import get_traced_memory


class Position:
    """information about the relevant item in a ranking"""
    position:int = None
    did:str = None
    grades:dict[int,float] = {}

    def __init__(self,position: int,did: str,grades: dict[int,float]):
        self.position = position
        self.did = did
        self.grades = grades

    def is_valid(self,grade:float=1.0,subtopic:int=0) -> bool:
        if (subtopic in self.grades) and (self.grades[subtopic] >= grade):
            return True
        return False
    
    def get_grade(self,subtopic:int=0) -> float:
        if (subtopic in self.grades):
            return self.grades[subtopic]
        return 0.0


class RelevanceVector:
    """relevant item positions"""
    qid:str = ""
    num_retrieved:int = 0
    positions:list[Position] = []
    grades:list[float] = []
    subtopics:list[int] = []
    dids:list[str] = []
    grade_histogram = {}
    _cached_vector:list[int] = []
    _cached_rel_ret:int = 0

    def __init__(self,qid:str,num_retrieved:int):
        self.qid = qid
        self.num_retrieved = num_retrieved
        self.positions = []
        self.grades = []
        self.subtopics = []
        self.dids = []
        self._cached_vector = []
        self._cached_rel_ret = 0
    
    def append(self,position:int,did:str,grades=None):
        self._cached_vector = []
        self._cached_rel_ret = 0
        if grades is not None:
            for st,grade in grades.items():
                if not st in self.subtopics:
                    self.subtopics.append(st)
                if not grade in self.grades:
                    self.grades.append(grade)
                if not did in self.dids:
                    self.dids.append(did)
            if 0 in grades:
                grade = grades[0]
                if not grade in self.grade_histogram:
                    self.grade_histogram[grade] = 0
                self.grade_histogram[grade] = self.grade_histogram[grade] + 1
            pos:Position = Position(position,did,grades)
            self.positions.append(pos)
    
    def vector(self,grade:float=None,subtopic:int=None) -> list[int]:
        if len(self._cached_vector) > 0:
            return self._cached_vector
        retval:list[int] = []
        subtopic = 0 if subtopic is None else subtopic
        if len(self.grades) == 0:
            sys.stderr.write(f"no grade information for qid: {self.qid}\n")
        grade = min(self.grades) if grade is None else grade
        rel_ret: int = 0
        for pos in self.positions:
            if pos.is_valid(grade,subtopic):
                if (pos.position is not None):
                    retval.append(pos.position)
                    rel_ret = rel_ret + 1
        retval.sort()
        for pos in self.positions:
            if pos.is_valid(grade,subtopic):
                if (pos.position is None):
                    retval.append(None)
        self._cached_vector = retval
        self._cached_rel_ret = rel_ret
        return retval

    def rel_ret(self,grade:float=None,subtopic:int=None) -> int:
        if len(self._cached_vector) == 0:
            self.vector(grade,subtopic)
        return self._cached_rel_ret

    def stvector(self,position:int = 0, reverse:bool = False, grade:float=None) -> list[int]:
        self._cached_vector = []
        self._cached_rel_ret = 0
        processed_position = position if (reverse is False) else -1 * (position+1)
        retval:list[int] = []
        num_subtopics = len(self.subtopics)
        retval_tail = []
        for i in range(num_subtopics):
            st = self.subtopics[i]
            if st != 0:
                pos = self.vector(grade,st)
                if (position < len(pos)):
                    if pos[processed_position] is not None:
                        retval.append(pos[processed_position])
                    else:
                        retval_tail.append(None)
                else:
                    return None
        if (len(retval)+len(retval_tail)) == 0:
            return None
        retval.sort()
        retval += retval_tail
        return retval

    def grade_vector(self,subtopic:int=None) -> list[tuple[int,float]]:
        retval:list[tuple[int,float]] = []
        subtopic = 0 if subtopic is None else subtopic
        for pos in self.positions:
            if (pos.position != None):
                grade = pos.get_grade(subtopic)
                if grade > 0.0:
                    t = (pos.position,grade)
                    retval.append(t)
        retval.sort(key=lambda x: x[0])
        return retval

