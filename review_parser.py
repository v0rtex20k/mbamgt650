import data # local dir w/ review data

import os
import datetime as dt
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Older versions of python (< 3.7)
    import importlib_resources as pkg_resources # type: ignore


class Review(BaseModel):
    score: float = Field(
        title='Score',
        description='score from 0-5 assigned by the reviewer',
        ge=0,
        le=5,
    )
    date: float = Field(
        title='Date',
        description='the date of publication',
    )
    header: str = Field(
        title='Header',
        description='the one-line header',
    )
    credentials: str = Field(
        title='Credentials',
        description="the reviewer's credentials",
    )
    location: Optional[str] = Field(
        title='Location',
        description="where the reviewer worked",
    )
    content: Optional[str] = Field(
        title='Content',
        description="the content of the review",
    )
    pros: Optional[str] = Field(
        title='Pros',
        description="The pros identified by the reviewer, if any",
    )
    cons: Optional[str] = Field(
        title='Cons',
        description="The cons identified by the reviewer, if any",
    )
    advice_to_mgmt: Optional[str] = Field(
        title='Advice To Management',
        description="The reviewer's advice to management, if any",
    )
    origin: str = Field(
        title='Origin',
        description="The origin of the review",
    )

    @validator("date", pre=True)
    def parse_date(cls, value):
        def __parse(strp_str: str):
            return dt.datetime(*list(map(int, dt.datetime.strptime(value, strp_str).strftime('%Y-%m-%d').split("-")))).timestamp()
        try:
            return  __parse('%B %d, %Y')
        except ValueError:
            return __parse('%b %d, %Y')
            


    def add_content(self, new_content: str):
        self.content += ('. ' if not self.content.endswith(".") else ' ') + new_content.capitalize()


def glassdoor(raw_reviews: List[str])-> List[Review]:
    reviews: List[Review] = []
    for r in raw_reviews:
        lines = r.replace('\'', '').replace('\"', '').split('\n')
        score, creds = lines.pop(0).strip().split(maxsplit=1)
        header = lines.pop(0).strip()
        date = lines.pop(0).strip().split(" - ")[0]
        pros, cons, advice = None, None, None
        try:
            pros = lines.pop(0).strip().removeprefix("Pros - ")
        except IndexError:
            pass  # this review must not contain any pros
        try:
            cons = lines.pop(0).strip().removeprefix("Cons - ")
        except IndexError:
            pass  # this review must not contain any cons
        try:
            advice = lines.pop(0).strip().removeprefix("Advice to Management - ")
        except IndexError:
            pass  # this review must not contain any cons
        reviews.append(Review(score=float(score),
                              date=date,
                              header=header,
                              credentials=creds,
                              location=None,
                              content=None,
                              pros=pros,
                              cons=cons,
                              advice_to_mgmt=advice,
                              origin="glassdoor"))
    
    print(f"Parsed {len(reviews)} glasdoor reviews!")
    return reviews

def indeed(raw_reviews: List[str])-> List[Review]:
    reviews: List[Review] = []
    for r in raw_reviews:
        lines = r.replace('\'', '').replace('\"', '').split('\n')
        first_line = lines.pop(0)
        try:
            score, header = first_line.strip().split(" Stars - ")
        except ValueError:
            try:
                score, header = first_line.strip().split(" Star - ")
            except ValueError:
                reviews[-1].add_content(first_line)
                continue
        creds, loc, date = lines.pop(0).strip().split(" - ")
        content = lines.pop(0).strip()
        pros, cons = None, None
        try:
            pros = lines.pop(0).strip().removeprefix("Pros - ")
        except IndexError:
            pass  # this review must not contain any pros
        try:
            cons = lines.pop(0).strip().removeprefix("Cons - ")
        except IndexError:
            pass  # this review must not contain any cons
        reviews.append(Review(score=float(score),
                              date=date,
                              header=header,
                              credentials=creds,
                              location=loc,
                              content=content,
                              pros=pros,
                              cons=cons,
                              advice_to_mgmt=None,
                              origin="indeed"))
    
    print(f"Parsed {len(reviews)} indeed reviews!")
    return reviews




def load_reviews(sep: str="\n\n")-> List[Review]:
    """Convenience func to load in all the reviews from our data directory.
    Please note that each review MUST be separated by sep, which I've set to
    default to an empty line, and there must be a matching function for each 
    data-file name (i.e glassdoor <--> glassdoor[List[str], List[Review]] )

    Args:
        sep (str): the separator between each review
    Returns:
        List[Dict[str, str]]: All the processed reviews
    """
    all_reviews: List[Dict[str, str]] = []
    for file in pkg_resources.contents(data):
        if not file.endswith(".txt"):
            # print("Ignoring ", file)
            continue
        
        try:
            parse_func: str = globals()[file.lower().split('.')[0]]
            all_reviews.extend(parse_func(pkg_resources.read_text(data, file).split(sep)))
        except KeyError:
            print(f"Unable to parse \"{file}\" reviews - local function \"{parse_func}\" does not exist.")
    return all_reviews

def load_map():
    for file in pkg_resources.contents(data.map):
        if file.endswith(".shp"):
            return os.path.join(data.map.__path__[0], file)

def main():
    all_reviews = load_reviews()
    

if __name__ == "__main__":
    main()