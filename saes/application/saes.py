from abc import ABC
from typing import List

from lxml import etree
from bs4 import BeautifulSoup

from courses.domain.model.course import Course, session, ScheduleCourse, CourseAvailability
from subjects.domain.model.subject import Subject

class SAESService(ABC):
  def get_courses(self, document) -> List[Course]:
    pass
  
class SaesService(SAESService):
  def __init__(
      self,
    ):
    pass
  
  def get_courses(self, document) -> List[Course]:
    courses: List[Course] = []

    dom = etree.HTML(str(BeautifulSoup(document, 'html.parser', from_encoding='utf8')))
    raw_courses = dom.xpath('//table[@id="ctl00_mainCopy_dbgHorarios"]//tr')[1:]
    props = dom.xpath('//select/option[@selected="selected"]/@value')
    
    career: str = props[0]
    shift: str = props[1]
    plan: str = props[2]
    level: str = props[3]


    for idx, raw_course in enumerate(raw_courses):
      sequence = raw_course.xpath('./td/text()')[0].strip().upper()
      teacher_name = raw_course.xpath('./td/text()')[2].strip().upper()
      if sequence[0] != level or sequence[3] != level:
        continue

      sessions = get_sessions(raw_course)
      
      schedule_course: ScheduleCourse = ScheduleCourse()
      schedule_course['monday'] = sessions[0]
      schedule_course['tuesday'] = sessions[1]
      schedule_course['wednesday'] = sessions[2]
      schedule_course['thursday'] = sessions[3]
      schedule_course['friday'] = sessions[4]
      
      course = Course(
        id=idx,
        sequence=sequence,
        subject=raw_course.xpath('./td/text()')[1],
        teacher=teacher_name,
        schedule=schedule_course,
        course_availability=40,
      )

      courses.append(course)

    return courses
  
  def get_course_availability(self, document) -> List[CourseAvailability]:
    availabilities: List[CourseAvailability] = []
    
    dom = etree.HTML(str(BeautifulSoup(document, 'html.parser', from_encoding='utf8')))
    raw_courses = dom.xpath('//table[@id="ctl00_mainCopy_GrvOcupabilidad"]//tr')[1:]
    
    for raw_course in raw_courses:
      sequence: str = raw_course.xpath('./td/text()')[0].strip().upper()
      subject: str = raw_course.xpath('./td/text()')[2].strip().upper()
      course_avalibility = int(raw_course.xpath('./td/text()')[6].strip())
    
    
      a = CourseAvailability(
        sequence=sequence,
        subject=subject,
        course_availability=course_avalibility
      )
      availabilities.append(a)
      
    return availabilities
  
  def get_subjects(self, document) -> List[Subject]:
    subjects: List[Subject] = []
    
    dom = etree.HTML(str(BeautifulSoup(document, 'html.parser', from_encoding='utf8')))
    props = dom.xpath('//select/option[@selected="selected"]/@value')
    raw_subjects = dom.xpath('//table[@id="ctl00_mainCopy_GridView1"]//tr')[1:]
    
    career: str = props[0]
    plan: str = props[1]
    
    for raw_subject in raw_subjects:
      fields = raw_subject.xpath('./td/text()')
      
      level: int = int(fields[0])
      key: str = fields[1]
      name: str = fields[2]
      required: bool = True if fields[3].strip().upper() == 'OBLIGATORIA' else False
      credits_required: float = float(fields[4])
      
      subject = Subject(
        career=career,
        plan=plan,
        level=level,
        key=key,
        name=name,
        required=required,
        credits_required=credits_required
      )
      
      subjects.append(subject)
      
    return subjects 
    
def get_sessions(raw_course) -> session:
  sessions: List[session] = []
  
  days = raw_course.xpath('./td/text()')[5:-1]
  for day in days:
    day: str = day.strip()
    if day:
      sessions.append(tuple(day.split('-')))
    else:
      sessions.append(None)
      
  return sessions
