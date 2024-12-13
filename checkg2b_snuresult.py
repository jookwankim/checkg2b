import requests
import time
from bs4 import BeautifulSoup
import hashlib
import pandas as pd
import time
from datetime import datetime

# 웹페이지에서 HTML을 가져오는 함수
def fetch_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # 상태 코드가 200이 아닐 경우 예외 발생
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
        return None

# HTML에서 테이블을 추출하는 함수
def extract_table_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # 테이블 요소를 찾기
    # 공고
    # table = soup.find('table', {'class': 'table_list_tbidTbl'})
    # 개찰결과  table_list table_list_integrationTbl
    table = soup.find('table', {'class': 'table_list_integrationTbl1'})
    
    if not table:
        print("Table not found in the HTML.")
        return None
    
    # 테이블 헤더 추출
    headers = [th.text.strip() for th in table.find_all('th')]
    
    # 테이블 데이터 추출
    rows = []
    for tr in table.find_all('tr')[1:]:  # 첫 번째는 헤더이므로 제외
        cells = [td.text.strip() for td in tr.find_all('td')]
        if cells:
            rows.append(cells)
            print("\a")
            #print(cells)
            #공고번호, 공고명만 출력
            #print(cells[1] + ' ' + cells[3])
    
    return headers, rows

# 데이터를 엑셀로 저장하는 함수
def save_to_excel(headers, rows, file_name):
    if headers and rows:
        df = pd.DataFrame(rows, columns=headers)
        df.to_excel(file_name, index=False)
        print(f"Table data has been saved to {file_name}.")
    else:
        print("No data to save.")
        
        
# 콘텐츠의 해시 값을 계산하여 변경 사항을 추적
def hash_content(content):
    if isinstance(content , list):
        # ['용역', '20241021996-00', '일반', '본부 사옥 냉,온정수기 임차 유지관리', '국민건강보험공단', '국민건강보험공단', '일반(총액)', '2024/10/21 18:09(2024/10/30 11:00)', '', '지문투찰']
        # content[1] is 공고번호
        
        # list 모든 문자열 연결
        joinedContent = "".join(content)
        
        #print ("join:" + joinedContent);
        return hashlib.md5(joinedContent.encode('utf-8')).hexdigest()
    else:
        return hashlib.md5(content.encode('utf-8')).hexdigest()

# 변경 사항을 감지하는 함수
def check_for_changes(rows, old_hash):
    
    new_hash = hash_content(rows)
    
    dt = datetime.now().strftime('%x %X')
    
    gonggoNo = None
    
    if isinstance(rows, list):
        gonggoNo = rows[1]
    else:
        gonggoNo = rows
    
    if new_hash != old_hash:
        print(f"Content has changed on {dt} [{gonggoNo}]")
        return new_hash, True
    else:
        print(f"No changes detected on {dt} [{gonggoNo}]")
        return old_hash, False        

# 메인 함수
def main():
    #2025년~2027년 서울대학교 IT서비스 통합 운영 유지관리 사업
    url = 'https://www.g2b.go.kr:8101/ep/result/listPageIntegrationBidResult.do?bidno=20241031974'  # 여기에 웹페이지 URL을 입력
    #https://www.g2b.go.kr:8101/ep/result/listPageIntegrationBidResult.do?searchType=1&bidSearchType=2&taskClCds=5&bidNm=%B0%E6%B1%E2%B5%B5&searchDtType=2&fromBidDt=&toBidDt=&fromOpenBidDt=2024%2F12%2F10&toOpenBidDt=2025%2F01%2F09&radOrgan=2&instNm=%B0%E6%B1%E2%B5%B5&instSearchRangeType=1&refNo=&area=&areaNm=&strArea=&orgArea=&industry=&industryCd=&upBudget=&downBudget=&budgetCompare=&detailPrdnmNo=&detailPrdnm=&procmntReqNo=&intbidYn=&regYn=Y&recordCountPerPage=30
    # 용역, 국민건강보험공단, ~2024/10/31
    #url = 'https://www.g2b.go.kr:8101/ep/tbid/tbidList.do?searchType=1&bidSearchType=1&taskClCds=5&bidNm=&searchDtType=1&fromBidDt=2024%2F09%2F23&toBidDt=2024%2F10%2F31&setMonth1=1&fromOpenBidDt=&toOpenBidDt=&radOrgan=2&instNm=%B1%B9%B9%CE%B0%C7%B0%AD%BA%B8%C7%E8%B0%F8%B4%DC&instSearchRangeType=1&refNo=&area=&areaNm=&strArea=&orgArea=&industry=&industryCd=&upBudget=&downBudget=&budgetCompare=&detailPrdnmNo=&detailPrdnm=&procmntReqNo=&intbidYn=&regYn=Y&recordCountPerPage=10'
    #output_file = 'D:/temp/bid_table_data.xlsx'
    interval = 300
    
    old_hash = None
    
    cnt = 0;
    while True:
        # HTML 가져오기
        html_content = fetch_html(url)
        
        if html_content:
            # 테이블 데이터 추출
            headers, rows = extract_table_data(html_content)
            
            #if (cnt == 0):
            #print(headers)
            #print (rows)
            
            #cnt = cnt+1
            
            #if headers and rows:
            #    # 엑셀 파일로 저장
            #    save_to_excel(headers, rows, output_file)
            
            #if old_hash is None:
            #    old_hash = hash_content(rows[0])
            #else:
                # 이후 변경 사항 체크
            #print (rows[0])
            old_hash, changed = check_for_changes(rows[0], old_hash)
                
            if changed:
                for row in rows:
                #    print(f'{row[1]}    {row[3]}    {row[9]}')
                    print(row)
                #else:
                #    print (old_hash)
            
        time.sleep(interval)  # interval 시간 만큼 대기                
        #break

if __name__ == "__main__":
    main()