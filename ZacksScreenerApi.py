import csv
from pprint import pprint

import requests


class ZacksScreenerApi:
    URL = "https://screener-api.zacks.com/"
    KEY = "0675466c5b74cfac34f6be7dc37d4fe6a008e212e2ef73bdcd7e9f1f9a9bd377"

    class ScreenerArgs:
        MarketCap = "MarketCap"
        Exchange = "Exchange"
        FiscalYear = "FiscalYear"
        Sector = "Sector"
        Industry = "Industry"
        EPS_LAST = "EPS_LAST"
        EPS_F0 = "EPS_F0"
        EPS_F1 = "EPS_F1"
        EPS_F2 = "EPS_F2"
        PE = "PE"
        PE_F1 = "PE_F1"
        PE_F2 = "PE_F2"
        PEG = "PEG"
        NEXT_EPS_REPORT = "NEXT_EPS_REPORT"
        ROE = "ROE"
        REVENUE_HISTORICAL_GROWTH = "REVENUE_HISTORICAL"
        REVENUE_F1 = "REVENUE_F1"
        REVENUE_ANNUAL = "REVENUE_ANNUAL"
        DIVIDEND_YIELD = "DIVIDEND_YIELD"

    IdMap = {
        ScreenerArgs.MarketCap: 12010,
        ScreenerArgs.Exchange: 11005,
        ScreenerArgs.Sector: 11025,
        ScreenerArgs.Industry: 11030,
        ScreenerArgs.EPS_LAST: 17005,
        ScreenerArgs.EPS_F0: 19045,
        ScreenerArgs.EPS_F1: 19055,
        ScreenerArgs.EPS_F2: 19070,
        ScreenerArgs.PE: 22005,
        ScreenerArgs.PE_F1: 22010,
        ScreenerArgs.PE_F2: 22015,
        ScreenerArgs.PEG: 22020,
        ScreenerArgs.NEXT_EPS_REPORT: 17055,
        ScreenerArgs.ROE: 23005,
        ScreenerArgs.REVENUE_HISTORICAL_GROWTH: 21010,
        ScreenerArgs.REVENUE_F1: 21015,
        ScreenerArgs.REVENUE_ANNUAL: 24005,
        ScreenerArgs.DIVIDEND_YIELD: 25005,
    }

    CriteriaKeyMap = {
        ScreenerArgs.MarketCap: 8,
    }

    CriteriaName = {
        ScreenerArgs.MarketCap: "Market Cap (mil)",
    }

    def __init__(self):
        self._session = requests.Session()
        self._headers = {
            "Accept": "*/*;q=0.8",
            "Host": "screener-api.zacks.com",
            "User-Agent": "Mozilla/5.0 (Linux; Android 11; SAMSUNG SM-G973U) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/14.2 Chrome/87.0.4280.141 Mobile Safari/537.36",
        }
        self._init_session()

    def _init_session(self):
        path = f"{self.URL}?scr_type=stock&c_id=zacks&c_key={self.KEY}"
        self._session.get(path, headers=self._headers)

    def add_criteria(self, arg: str, value):
        c_key = self.CriteriaKeyMap[arg]
        get_path = f"{self.URL}getaddedcriteria.php?criteria_id=10000&criteria_key={c_key}&isfirstcount=0"
        self._session.cookies.set("CURRENT_POS", "new_screen")
        response = self._session.get(get_path, headers=self._headers)
        assert response.status_code == 200, f"Wrong status code: {response.status_code}"

        post_path = f"{self.URL}getrunscreendata.php"
        data = {
            "is_only_matches": 1,
            "is_premium_exists": 0,
            "is_edit_view": 0,
            "saved_screen_name": "",
            "tab_id": 1,
            "start_page": 1,
            "no_of_rec": 15,
            "sort_col": 2,
            "sort_type": "ASC",
            "operator[]": 6,
            "value[]": value,
            "p_items[]": self.IdMap[arg],
            "p_item_name[]": self.CriteriaName[arg],
            "p_item_key[]": c_key
        }
        response = self._session.post(post_path, data=data)
        assert response.status_code == 200, f"Wrong status code: {response.status_code}"
        assert response.content, "Should not be empty"

    def add_view(self, arg: str):
        _id = self.IdMap[arg]
        path = f"{self.URL}reset_param.php?scr_irem_id={_id}&mode=add"
        resp = self._session.get(path, headers=self._headers)
        assert resp.status_code == 200, f"Wrong status code: {resp.status_code}"
        content = resp.content.decode("utf-8")
        assert content == "added", f"Unexpected content: {content}"

    def list(self):
        resp = self._session.get(f"{self.URL}export.php", headers=self._headers)
        assert resp.status_code == 200, f"Wrong status code: {resp.status_code}"
        decoded_content = resp.content.decode('utf-8')
        cr = csv.reader(decoded_content.splitlines(), delimiter=',', quotechar='"')
        return list(cr)


if __name__ == '__main__':
    screener_api = ZacksScreenerApi()
    screener_api.add_criteria(
        ZacksScreenerApi.ScreenerArgs.MarketCap, 1000
    )
    screener_api.add_view(ZacksScreenerApi.ScreenerArgs.PE)
    screener_api.add_view(ZacksScreenerApi.ScreenerArgs.PEG)
    pprint(screener_api.list())
