from selenium import webdriver
from selenium.webdriver.common.by import  By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from time import sleep
from bs4 import BeautifulSoup
import schedule
import datetime
import os
DataFilePos = "./data.json"
KickNameList = list()
Log = ""
Cookie = list()
BaseDataFileFatherName = "Test_1"





def readData( filepos ) :
    with open( filepos ) as f :
        return f.read();
def readJson ( filepos  ) :
    with open( filepos  ) as f :
        data =json.loads( f.read() );
    return data;
def WriteData( filepos, Data ) :
    print( f"Ouptut Data into file {filepos}..." );
    with open( filepos, 'w', encoding="utf-8" ) as f : 
        f.write( Data  );

UnitData = readJson( DataFilePos  );





def Login(driver) :
    """login"""

    driver.get( UnitData['url'][ 'login' ] );

    try: 
        lgcookie = readJson( f'./{BaseDataFileFatherName}/cookie.json' );
        for c in lgcookie :
            driver.add_cookie( {'name':c['name'], 'value':c['value']} );
    except:
        print("No Cookie Now")

    driver.refresh();
    if driver.current_url == "https://dandanjudge.fdhs.tyc.edu.tw/" :
        Cookie = driver.get_cookies()
        print(Cookie);
        WriteData(f'./{BaseDataFileFatherName}/cookie.json', json.dumps(Cookie, indent=4, ensure_ascii=False));
        return "Login Sucess"
    
    
    AccountName = input("Your account:");
    AccountEle = driver.find_element(By.CSS_SELECTOR ,'div.col-md-4:nth-child(2) > form:nth-child(1) > div:nth-child(1) > div:nth-child(2) > input:nth-child(2)'  ) ;
    AccountEle.send_keys( AccountName );


    PassWordName = input("your password:")
    PasswordEle = driver.find_element( By.XPATH, '//*[@id="passwd"]' );
    PasswordEle.send_keys( PassWordName )

    driver.find_element( By.XPATH,'/html/body/div[4]/div[2]/div[2]/form/button[1]' ).click();

    #"""add Cookie"""
    #print("Adding Cookie");
    #print( UnitData[ 'cookie' ] )
    #for (name, value) in UnitData[ 'cookie' ].items() :
       ##print( f"(name: {name}, value: {value})" );
       ##driver.add_cookie({"name": name, "value": value});
    #
    #driver.get( UnitData[ 'url' ]  );
    sleep(5)
    if driver.current_url == "https://dandanjudge.fdhs.tyc.edu.tw/" :
        Cookie = driver.get_cookies()
        print(Cookie);
        WriteData(f'./{BaseDataFileFatherName}/cookie.json', json.dumps(Cookie, indent=4, ensure_ascii=False));
        print("Login Sucess")
        return "Login Sucess"
    else :
        print( "Login Fail" )
        return "Login Fail"




def BaseDataAnaly(soup :BeautifulSoup, BaseDataDic) :
    problem_cnt = 0
    for val in soup.find_all( 'td' ) :
        if val.find( 'div' ) == None :
            BaseDataDic[str(val.text)  ] = True;
        else :
            problem_cnt += 1
            Problem = val.find('a')
            Score = val.find('span').text[:-1]
            ProblemHref = Problem['href'];
            ProblemName = Problem['title'];
            #print( ProblemHref, ProblemName, Score )
            BaseDataDic[ f'Problem_{problem_cnt}' ] = {
                "Score": Score,
                "Name": ProblemName,
                "Href": ProblemHref
            }


    return BaseDataDic

def stringNorm(st: str) :
    return st.replace(' ', '').replace('\n', '').replace('\t', '');

def UsrDataAnaly(soup, UsrDataDic) :
    for PerUsr in soup :
        lst = PerUsr.find_all('td', recursive=False)
        

        """Name"""
        Profile = lst[ 1 ];

        #print(Profile.find('div'))
        Name_Link = Profile.find( 'div' ).find('a');
        Name = Name_Link[ 'title' ]
        Link = Name_Link[ 'href' ]
        #print( Name, Link )


        NickName = Profile.find('div').find_all('span')[1].text.strip(); 

        SubmitHistory = Profile.find('a', recursive=False)['href'].strip();
        School = ""
        try:
            School = Profile.find('span', recursive=False).text.strip()
        except:
            pass

        #print(NickName, SubmitHistory, School)


        """Problem"""
        Problems = lst[2:-4]
        problemCnt =  0
        ProblemDic = dict();
        for problem in Problems :
            problemCnt += 1
            if problem.find( 'img' ) :
                ProblemDic[ f"Problem{problemCnt}" ] = 100
            else :
                score = problem.find('div').text
                score = stringNorm(score)
                if score == '-' :
                    score = 0;
                else :
                    score = score[:-1]

                ProblemDic[ f"Problem_{problemCnt}" ] = score
        #print(ProblemDic)
                
        

        """TatalScore"""

        TatalScore = stringNorm(lst[-4].find('div').text)[:-1]
        #print(TatalScore)

        """Correct Problem"""
        CorrectProblem_ = lst[-3].find('a');
        CorrectProblem_Href = CorrectProblem_['href']
        CorrectProblem_Cnt = stringNorm(CorrectProblem_.text);
        #print( CorrectProblem_Href, CorrectProblem_Cnt )

        """Penalty"""
        Penalty = stringNorm(lst[-2].text)


        """Ranking list"""

        Rank = stringNorm(lst[-1].text)
        

        if Name in KickNameList :
            if UsrDataDic[ Name ][ 'Time' ] <= UnitData[ 'TimeLimit' ] :
                print(f"Error Happen,{Name} Time less")
                print(UsrDataDic[Name][ 'Time' ], UnitData['TimeLimit'])

            TimePass = UsrDataDic[ Name ][ 'Time' ]
        else :
            TimePass = ( 0 if not ( Name in UsrDataDic ) else  UsrDataDic[ Name ]['Time'] + 1)
        
        UsrDataDic[ Name ] = {
                "Profile" : {
                    "Name": str(Name),
                    "Link":str(Link),
                    "School": str(School),
                    "Id": str(Link)[str(Link).find("UserStatistic?id=")+len("UserStatistic?id="):]
                },
                "SubmitHistory": str(SubmitHistory),
                "TatalScore": int(TatalScore),
                "ACProblem": {
                    "Href": str(CorrectProblem_Href),
                    "Count": int(CorrectProblem_Cnt)
                },
                "Penalty": int(Penalty),
                "Rank" :int(Rank),
                "Time": int(TimePass)
        }

        UsrDataDic[Name]["Problems"] = dict();
        for (key, value) in ProblemDic.items() :
            UsrDataDic[Name]["Problems"][key] =int( value );
    
    
    return UsrDataDic


def KickPeopleFliter(UsrDataDic) :
    AppearList = list()
    for (key,value) in UsrDataDic.items() :
        if value[ "Time" ] > UnitData[ "TimeLimit"  ] and not ( key in KickNameList  ) :
            KickNameList.append( key  );
            AppearList.append( key  )
    return AppearList 

def KickPeople(KickList: list, UsrDataDic: dict, driver) :
    print(f"In Kick People-{len(KickList)}");

    driver.get( UnitData[ 'url' ][ 'Edit' ] );

    for name in KickList :
        Id = UsrDataDic[ name ][ 'Profile' ][ 'Id' ];
        print( f"kick {name}-{Id}");
        SelectString = f'button[data-qs*="action=finish&userid={Id}"]';
        print(driver.find_elements( By.CSS_SELECTOR, SelectString));
        Button = driver.find_element( By.CSS_SELECTOR, SelectString );
        print(Button);
        
        classname = 'btn-primary'
        FirstData = driver.find_elements( By.CLASS_NAME, classname)
        Button.click();
        sleep(1);
        SecondData = driver.find_elements( By.CLASS_NAME, classname);
        print(SecondData)
        print(list(set(SecondData).difference(FirstData)));
        list(set(SecondData).difference(FirstData))[0].click();
        sleep(2);


    driver.get( UnitData[ 'url' ][ 'Ranking' ] );
    #ata-qs="action=finish&userid=458&contestid=209"


        
def DataAnaly(soup, DataFile, UsrDataDic, BaseDataDic) :
    if( not os.path.isdir(DataFile) ) :
        os.makedirs(DataFile);

    pthFile = os.path.join(DataFile, "Final_data")
    if( not os.path.isdir(pthFile) ) :
        os.makedirs(pthFile);

    soup = soup.find( 'tbody' )
    BaseData = soup.find_all('tr')[0];
    UsrData = soup.find_all('tr')[1:];

    BaseDataDic = BaseDataAnaly(BaseData, BaseDataDic);
    UsrDataDic = UsrDataAnaly(UsrData, UsrDataDic);
    FinalData = {
            "BaseData":BaseDataDic,
            "UsrData":UsrDataDic
    };
    #print(FinalData)

    KickList = KickPeopleFliter(UsrDataDic) 

    if len(KickNameList) == len(UsrDataDic) :
        print("There is no people in the contest now")



    TimeNow = datetime.datetime.today().strftime("(%H_%M_%S)-");
    #WriteData( f'./{DataFile}/{TimeNow}ContestData.json', json.dumps( FinalData, indent=4, ensure_ascii=False) );
    #WriteData( f'./{pthFile}/Final.json', json.dumps(FinalData, indent=4, ensure_ascii=False) );
    #WriteData( f'./{pthFile}/KickList.json', json.dumps(KickNameList, indent=4, ensure_ascii=False) );

    return KickList, FinalData;
    

"""

我預計是要把它變成可以自動在參賽者進入比賽 n 分鐘後自動把他們踢掉,

並紀錄下他們的成績

每分鐘程式跑一遍

紀錄下是否有新的人加入

還有確認他們目前的時間

"""

def StartGetData(driver, UsrDataDic, BaseDataDic) :
    print(f"""
    {datetime.datetime.today().strftime("(%H:%M:%S)")}: Getting Data...
    """)
    driver.refresh();
    soup = BeautifulSoup(driver.page_source, 'html5lib').find('table');
    #soup = BeautifulSoup(readData('./WebPageHtml.html'), 'html5lib');

    FinalData = dict()
    kicklist, FinalData =DataAnaly( soup, BaseDataFileFatherName, UsrDataDic, BaseDataDic );
    #print(FinalData)

    #KickPeople( kicklist, UsrDataDic, driver);
    print(f"""
    {datetime.datetime.today().strftime("(%H:%M:%S)")}: End Getting Data...
    """)
    return FinalData;

def MainLoop() :
    print("Start Main Loop")

    #UnitData[ 'url' ][ 'Ranking' ] += f"?contestid={UnitData[ 'contestid' ]}"
    #UnitData[ 'url' ][ 'Edit' ] += f"?contestid={UnitData[ 'contestid' ]}"

    UsrDataDic = dict()
    BaseDataDic = dict()
    FinalData = dict()    
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = webdriver.Chrome(options=options);
    Login(driver);
    import copy

    global UnitData
    tmpUnitData = copy.deepcopy(UnitData);
    for ContestId in tmpUnitData[ 'contestid' ] :
    #for ContestId in range(229,230) :
        try: 
            #driver.get( UnitData[ 'url' ][ 'Ranking' ] + f"?contestid={ContestId}" )
            UnitData[ 'url' ][ 'Ranking' ] = tmpUnitData[ 'url' ][ 'Ranking' ] + f"?contestid={ContestId}"
            UnitData[ 'url' ][ 'Edit' ] = tmpUnitData[ 'url' ][ 'Edit' ] + f"?contestid={ContestId}"
            UsrDataDic[ ContestId ] = dict()
            BaseDataDic[ ContestId ] = dict()
            FinalData[ ContestId ] = dict()
            driver.get( UnitData[ 'url' ][ 'Ranking' ])
            #print( UnitData[ 'url' ][ 'Ranking' ])
            FinalData[ContestId] = StartGetData(driver, UsrDataDic[ ContestId ], BaseDataDic[ ContestId ]) ;

            UnitData = copy.deepcopy(tmpUnitData);
            #print(UnitData)
            sleep(0.3);
        except :
            pass

    WriteData( f'./{BaseDataFileFatherName}/Final.json', json.dumps(FinalData, indent=4, ensure_ascii=False) );
    #driver.get( UnitData[ 'url' ][ 'Ranking' ] )
    #schedule.every().second.do( lambda: StartGetData(driver, UsrDataDic, BaseDataDic) );

    #StartGetData(driver, UsrDataDic, BaseDataDic);
    #while True :
    #    schedule.run_pending();
    
    
if __name__ == '__main__' :
    """Reading Data"""
    if( not os.path.exists( f'./{BaseDataFileFatherName}' ) ) :
        os.mkdir(f'./{BaseDataFileFatherName}')
    
    # driver = webdriver.Firefox()
    # Login(driver)
    # driver.get(UnitData['url']['Edit'])
    # #WriteData( "./WebEdit.html", driver.page_source )

    #try :
    MainLoop();
    #except :
    #    WriteData('./Log.txt', Log)

    
    """Init Driver"""
    """
    driver = webdriver.Firefox()
    #LoginStatus = Login(driver)
    #print( LoginStatus  );
    #driver.get('https://google.com');
    #driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/input').send_keys('hello, world');
    #sleep(3)
    #driver.close()
    #driver.quit()
    driver.set_window_position(0, 0);
    driver.get( UnitData[ 'url' ][ 'Contest' ] )

    #while( True ) :
        #print(driver.get_window_position())
        #sleep(1)

    WebHtml = driver.page_source;
    """

    #target_data = str(soup.find( 'table' ))
    #print( target_data )

    #WriteText( "./WebPageHtml.html",  target_data);
    #driver.close();
    #driver.quit();
