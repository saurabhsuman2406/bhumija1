# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"
from __future__ import print_function
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from rasa_sdk.events import SlotSet, EventType
from youtube_search import YoutubeSearch
import re
import webbrowser
import datetime as dt 
import requests, json
import pandas as pd
import numpy as np
import sqlite3
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import warnings


#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []


class SearchVideoForm(Action):
    def name(self) -> Text:
        return "search_video_form"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        #dispatcher.utter_message("Type topic to search video?")
        required_slots = ["search_url"]

        for slot_name in required_slots:
            if tracker.slots.get(slot_name) is None:
                # The slot is not filled yet. Request the user to fill this slot next.
                return [SlotSet("requested_slot", slot_name)]

        # All slots are filled.
        return [SlotSet("requested_slot", None)]

class ActionVideoSubmit(Action):
    def name(self) -> Text:
        return "search_video_submit"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "Dict",
    ) -> List[Dict[Text, Any]]:
        video_key= tracker.get_slot("search_url")
        results = YoutubeSearch(video_key, max_results=10).to_json()
        print(tracker.get_slot("search_url"))
        video_ids = re.findall(r"watch\?v=(\S{11})", results)
        #video_url="https://www.youtube.com/watch?v=" + video_ids[1]
        dispatcher.utter_message("wait... Playing your video.")
        dispatcher.utter_message("https://www.youtube.com/watch?v=" + video_ids[1])
       # webbrowser.open("https://www.youtube.com/watch?v=" + video_ids[1])
        return []



        #print(video_ids)
        #for i in range(len(video_ids)):
        #    print("https://www.youtube.com/watch?v=" + video_ids[i])

class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_show_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text=f"{dt.datetime.now()}")

        return []



class SearchWeatherInfoForm(Action):
    def name(self) -> Text:
        return "location_entry_form"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        #dispatcher.utter_message("Type topic to search video?")
        required_slots = ["location"]

        for slot_name in required_slots:
            if tracker.slots.get(slot_name) is None:
                # The slot is not filled yet. Request the user to fill this slot next.
                return [SlotSet("requested_slot", slot_name)]

        # All slots are filled.
        return [SlotSet("requested_slot", None)]

class ActionWeatherLocationSubmit(Action):
    def name(self) -> Text:
        return "location_entry_to_know_weather_submit"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "Dict",
    ) -> List[Dict[Text, Any]]:
        BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"
        CITY = tracker.get_slot("location")
        
        API_KEY = "78a4249c15bac3a950d1dd4d4165c119"
        # upadting the URL
        URL = BASE_URL + "q=" + CITY + "&units=metric" + "&lang=hi" + "&APPID=" + API_KEY
        # HTTP request
        response = requests.get(URL)
        # checking the status code of the request
        if response.status_code == 200:
            # getting data in the json format
            data = response.json()
            # getting the main dict block
            main = data['main']
            # getting temperature
            temperature = main['temp']
            # getting the humidity
            humidity = main['humidity']
            # getting the pressure
            pressure = main['pressure']
            # weather report
            report = data['weather']
            dispatcher.utter_message(f"{CITY:-^30}")
            dispatcher.utter_message(f"Temperature: {temperature}")
            dispatcher.utter_message(f"Humidity: {humidity}")
            dispatcher.utter_message(f"Pressure: {pressure}")
            dispatcher.utter_message(f"Weather Report: {report[0]['description']}")
        else:
            # showing the error message
            print("Try after sometime.")




        #dispatcher.utter_message("Weather in your location")
        #dispatcher.utter_message(city)
       
        return []




#veterinary_centre_form
class VeterinaryCentreInfoForm(Action):
    def name(self) -> Text:
        return "veterinary_centre_form"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        #dispatcher.utter_message("Type topic to search video?")
        required_slots = ["veterinary_centre_State_Name", "veterinary_centre_District_Name" , "veterinary_centre_Block_Name" ]

        for slot_name in required_slots:
            if tracker.slots.get(slot_name) is None:
                # The slot is not filled yet. Request the user to fill this slot next.
                return [SlotSet("requested_slot", slot_name)]

        # All slots are filled.
        return [SlotSet("requested_slot", None)]

class ActionVeterinaryCentreInfoSubmit(Action):
    def name(self) -> Text:
        return "veterinary_centre_submit"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "Dict",
    ) -> List[Dict[Text, Any]]:
        conn = sqlite3.connect(r"rekha.db")
        State_Name=tracker.get_slot("veterinary_centre_State_Name")
        District_Name=tracker.get_slot("veterinary_centre_District_Name")
        BLOCK_Name=tracker.get_slot("veterinary_centre_Block_Name")
        dispatcher.utter_message(State_Name)
        dispatcher.utter_message(District_Name)
        dispatcher.utter_message(BLOCK_Name)
        q="select * from veterinary_centre where \"State Name\""+"like"+"\""+State_Name+"\""+ "AND \"District Name\"like"+"\""+District_Name+"\""+ " AND \"BLOCK Name\"like"+"\""+BLOCK_Name+"\""";"
        df = pd.read_sql_query(q, conn)
        if df.shape[0] >= 1:
            df.fillna('')
            df['Final']=df['Centre Name']+" "+df['Address']+" "+df['Centre Type']
            df.dropna(inplace=True)
            for i in df["Final"]:
                dispatcher.utter_message(i)
        else:
            dispatcher.utter_message("No Data")
        conn.close()
        return []


#Diagnostic_Laboratory_form
class DiagnosticLaboratoryInfoForm(Action):
    def name(self) -> Text:
        return "Diagnostic_Laboratory_form"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        #dispatcher.utter_message("Type topic to search video?")
        required_slots = ["Diagnostic_Laboratory_State_Name"]

        for slot_name in required_slots:
            if tracker.slots.get(slot_name) is None:
                # The slot is not filled yet. Request the user to fill this slot next.
                return [SlotSet("requested_slot", slot_name)]

        # All slots are filled.
        return [SlotSet("requested_slot", None)]

class ActionDiagnosticLaboratoryInfoSubmit(Action):
    def name(self) -> Text:
        return "Diagnostic_Laboratory_submit"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "Dict",
    ) -> List[Dict[Text, Any]]:
        conn = sqlite3.connect(r"rekha.db")
        State_Name=tracker.get_slot("Diagnostic_Laboratory_State_Name")
        #dispatcher.utter_message(State_Name)
        #"select * from Diagnostic_Laboratory where \"State Name\" like "+"\"Bihar\";"
        q="select * from Diagnostic_Laboratory where \"State Name\" like "+"\""+State_Name+"\";"
        df = pd.read_sql_query(q, conn)
        if df.shape[0] >= 1:
            df.fillna('')
            df['Final']=df['District Name']+" "+df['ADDL']+" "+df['Person Name']+" "+df['Mobile']+""+df['Contact No']+""+df['EMail']+""+df['Address']
            df.dropna(inplace=True)
            for i in df["Final"]:
                dispatcher.utter_message(i)
        else:
            dispatcher.utter_message("No Data")
        conn.close()
        return []

# MSP_info_form
class MspInfoForm(Action):
    def name(self) -> Text:
        return "msp_info_form"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        #dispatcher.utter_message("Type topic to search video?")
        required_slots = ["msp_crop_name","msp_year"]

        for slot_name in required_slots:
            if tracker.slots.get(slot_name) is None:
                # The slot is not filled yet. Request the user to fill this slot next.
                return [SlotSet("requested_slot", slot_name)]

        # All slots are filled.
        return [SlotSet("requested_slot", None)]

class ActionDiagnosticLaboratoryInfoSubmit(Action):
    def name(self) -> Text:
        return "msp_info_form_submit"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "Dict",
    ) -> List[Dict[Text, Any]]:
        conn = sqlite3.connect(r"rekha.db")
        msp_crop_name=tracker.get_slot("msp_crop_name")
        msp_year=tracker.get_slot("msp_year") 
        #dispatcher.utter_message(State_Name)
        #"select * from Diagnostic_Laboratory where \"State Name\" like "+"\"Bihar\";"
        q="select * from msp where \"Commodity\" like "+"\""+msp_crop_name+"\" ;"
        df = pd.read_sql_query(q, conn)
        if df.shape[0] >= 1:
            
            if(msp_year=="2020-21"):
                df.fillna('')
                df['Final']="MSP for "+df['Commodity']+" "+df['Variety']+" is Rs. "+df['2020-21']+" in 2020-21"
                df.dropna(inplace=True)
            elif(msp_year=="2019-20"):
                df.fillna('')
                df['Final']="MSP for "+df['Commodity']+" "+df['Variety']+" is Rs. "+df['2019-20']+" in 2019-20"
                df.dropna(inplace=True)
            elif(msp_year=="2018-19"):
                df.fillna('')
                df['Final']="MSP for "+df['Commodity']+" "+df['Variety']+" is Rs. "+df['2018-19']+" in 2018-19"
                df.dropna(inplace=True)
            elif(msp_year=="2017-18"):
                df.fillna('')
                df['Final']="MSP for "+df['Commodity']+" "+df['Variety']+" is Rs. "+df['2017-18']+" in 2017-18"
                df.dropna(inplace=True)
            elif(msp_year=="2016-17"):
                df.fillna('')
                df['Final']="MSP for "+df['Commodity']+" "+df['Variety']+" is Rs. "+df['2016-17']+" in 2016-17"
                df.dropna(inplace=True)
            elif(msp_year=="2015-16"):
                df.fillna('')
                df['Final']="MSP for "+df['Commodity']+" "+df['Variety']+" is Rs. "+df['2015-16']+" in 2015-16"
                df.dropna(inplace=True) 
            elif(msp_year=="2014-15"):
                df.fillna('')
                df['Final']="MSP for "+df['Commodity']+" "+df['Variety']+" is Rs. "+df['2014-15']+" in 2014-15"
                df.dropna(inplace=True) 
            elif(msp_year=="2013-14"):
                df.fillna('')
                df['Final']="MSP for "+df['Commodity']+" "+df['Variety']+" is Rs. "+df['2013-14']+" in 2013-14"
                df.dropna(inplace=True) 
            elif(msp_year=="2012-13"):
                df.fillna('')
                df['Final']="MSP for "+df['Commodity']+" "+df['Variety']+" is Rs. "+df['2012-13']+" in 2012-13"
                df.dropna(inplace=True) 
            elif(msp_year=="2011-12"):
                df.fillna('')
                df['Final']="MSP for "+df['Commodity']+" "+df['Variety']+" is Rs. "+df['2011-12']+" in 2011-12"
                df.dropna(inplace=True) 
            elif(msp_year=="2010-11"):
                df.fillna('')
                df['Final']="MSP for "+df['Commodity']+" "+df['Variety']+" is Rs. "+df['2010-11']+" in 2010-11"
                df.dropna(inplace=True)
            else:
                dispatcher.utter_message("Data not available for the given input.")                                             
            for i in df['Final']:
                dispatcher.utter_message(i)
        else:
            dispatcher.utter_message("No Data")
        conn.close()
        return []

#soil moisture

class SoilDataInfor(Action):
    def name(self) -> Text:
        return "soil_moisture_database_open"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "Dict",
    ) -> List[Dict[Text, Any]]:
        conn = sqlite3.connect(r"rekha.db")
        q="select * from soil LIMIT 1;"
        df = pd.read_sql_query(q, conn)
        if df.shape[0] >= 1:
            df.fillna('')
            df['Final']="Location 1:"+df['moisture0']+" "+"Location 2:"+df['moisture1']+" "+"Location 3:"+df['moisture2']+" "+"Location 4:"+df['moisture3']+" "+"Location 5:"+df['moisture4']
            df.dropna(inplace=True)
            for i in df["Final"]:
                dispatcher.utter_message(i)
        else:
            dispatcher.utter_message("No Data")
        conn.close()
        return []

#soil nutrient info
class SoilDataInfor(Action):
    def name(self) -> Text:
        return "soil_nutrient_info_database_open"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "Dict",
    ) -> List[Dict[Text, Any]]:
        conn = sqlite3.connect(r"rekha.db")
        q="select * from nutrient LIMIT 1;"
        df = pd.read_sql_query(q, conn)
        if df.shape[0] >= 1:
            df.fillna('')
            df['Final']="Nitrogen:"+df['N']+" "+"Phosphorus:"+df['P']+" "+"Potassium:"+df['K']+" "+"Temperature:"+df['temperature']+" "+"Humidity:"+df['humidity']+" "+"PH:"+df['ph']
            df.dropna(inplace=True)
            for i in df["Final"]:
                dispatcher.utter_message(i)
        else:
            dispatcher.utter_message("No Data")
        conn.close()
        return []






class FertilizerCalulationLinkOpen(Action):
    def name(self) -> Text:
        return "fertilizer_calulation_link"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "Dict",
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message("Click on the given link for fertilizer caluclation!")
        dispatcher.utter_message("https://soilhealth.dac.gov.in/calculator/calculator")
        #webbrowser.open("https://soilhealth.dac.gov.in/calculator/calculator")
        return []


#Current_Daily_Price Form
class Current_Daily_PriceForm(Action):
    def name(self) -> Text:
        return "Current_Daily_Price_form"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        #dispatcher.utter_message("Type topic to search video?")
        required_slots = ["Current_Daily_Price_state","Current_Daily_Price_commodity"]

        for slot_name in required_slots:
            if tracker.slots.get(slot_name) is None:
                # The slot is not filled yet. Request the user to fill this slot next.
                return [SlotSet("requested_slot", slot_name)]

        # All slots are filled.
        return [SlotSet("requested_slot", None)]

class ActionCurrent_Daily_Price_form_submit(Action):
    def name(self) -> Text:
        return "Current_Daily_Price_form_submit"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "Dict",
    ) -> List[Dict[Text, Any]]:
        state=tracker.get_slot("Current_Daily_Price_state")
        commodity=tracker.get_slot("Current_Daily_Price_commodity")
        base_url="https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070?api-key=579b464db66ec23bdd000001d1eed6d0354e425669ecc5d1bbd1b43f&format=json&offset=0&limit=10000"
        response = requests.get(base_url)
        if(response.status_code==200):
            data = response.json()
            df=data['records']
            new = pd.DataFrame.from_dict(df)
            result =new.loc[new['state'].str.match(state[:2], case=False) & new['commodity'].str.match(commodity[:2], case=False)]
            if(result.size>=1):
                result['Final']="District: "+result['district']+"  Market: "+result['market']+"  Variety: "+result['variety']+" Arrival Date: "+result['arrival_date']+" Minimum Price:"+result['min_price']+" Maximum Price:"+result['max_price']+" Modal Price: "+result['modal_price']
                for i in result['Final']:
                    dispatcher.utter_message(i)
            else:
                dispatcher.utter_message("Data Not available !")
                #result        
        else:
            dispatcher.utter_message("Server error")
        
        
        
        return []

# crop_recommendation form_form
class CropRecomForm(Action):
    def name(self) -> Text:
        return "Crop_recommendation_form"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        #dispatcher.utter_message("Type topic to search video?")
        required_slots = ["nitrogen","potassium","phosphorus","temperature","humidity","ph","rainfall"]

        for slot_name in required_slots:
            if tracker.slots.get(slot_name) is None:
                # The slot is not filled yet. Request the user to fill this slot next.
                return [SlotSet("requested_slot", slot_name)]

        # All slots are filled.
        return [SlotSet("requested_slot", None)]

class ActioncropRecommendationSubmit(Action):
    def name(self) -> Text:
        return "crop_recommendation_submit"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "Dict",
    ) -> List[Dict[Text, Any]]:
        nitrogen=tracker.get_slot("nitrogen")
        potassium=tracker.get_slot("potassium")
        phosphorus=tracker.get_slot("phosphorus")
        temperature=tracker.get_slot("temperature")
        humidity=tracker.get_slot("humidity")
        ph=tracker.get_slot("ph")
        rainfall=float(tracker.get_slot("rainfall"))
        warnings.filterwarnings('ignore')
        PATH = 'Crop_recommendation.csv'
        df = pd.read_csv(PATH)
        features = df[['N', 'P','K','temperature', 'humidity', 'ph', 'rainfall']]
        target = df['label']
        labels = df['label']
        acc = []
        model = []
        Xtrain, Xtest, Ytrain, Ytest = train_test_split(features,target,test_size = 0.2,random_state =2)
        RF = RandomForestClassifier(n_estimators=20, random_state=0)
        RF.fit(Xtrain,Ytrain)
        data = np.array([[float(nitrogen),float(potassium),float(phosphorus),float(temperature),float(humidity),float(ph),float(rainfall)]])
#       data = np.array([[104,18, 30, 23.603016, 60.3, 6.7, 140.91]])
        prediction = RF.predict(data)
        r=prediction[0]
        #print(prediction)   
        dispatcher.utter_message("Bhoomija Recommends "+r+" for your farm")
        return []
