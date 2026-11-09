import requests
import os

# World Bank API - No API key required
BASE_URL = "https://api.worldbank.org/v2"

INDICATORS = {
    "1": ("GDP (Current US$)", "NY.GDP.MKTP.CD"),
    "2": ("Population (Total)", "SP.POP.TOTL"),
    "3": ("Life Expectancy (Years)", "SP.DYN.LE00.IN"),
    "4": ("Internet Users (% of population)", "IT.NET.USER.ZS"),
    "5": ("Capital City", "CAPITAL_CITY")
}

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def fetch_all_countries():
    try:
        response = requests.get(f"{BASE_URL}/country?format=json&per_page=300", timeout=10)
        data = response.json()
        return [c for c in data[1] if c['region']['value'] != 'Aggregates']
    except Exception as e:
        print(f"Error connecting to API: {e}")
        return []

def get_country_info(countries, user_input):
    user_input = user_input.lower()
    for c in countries:
        if c['name'].lower() == user_input or c['id'].lower() == user_input:
            return c
    return None

def fetch_indicator_data(country_code, indicator_code, years=5):
    url = f"{BASE_URL}/country/{country_code}/indicator/{indicator_code}?format=json&mrv={years}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if len(data) < 2 or not data[1]:
            return None
        return data[1]
    except Exception:
        return None

def display_country_data(country_info, indicator_data, indicator_name):
    print("\n" + "="*55)
    print(f"Country: {country_info['name']} ({country_info['id']})")
    print("="*55)
    
    if indicator_name == "Capital City":
        capital = country_info['capitalCity'] if country_info['capitalCity'] else 'N/A'
        print(f"\n--- Capital City ---")
        print(f"Capital: {capital}")
    else:
        print(f"\n--- {indicator_name} ---")
        print(f"{'Year':<10} | {'Value':<20}")
        print("-" * 35)
        for item in indicator_data:
            if item['value'] is not None:
                print(f"{item['date']:<10} | {item['value']:,.2f}")
                
    print("\n" + "="*55)

def display_compare(c1, c2, data1, data2, indicator_name):
    print("\n" + "="*75)
    print(f"Comparison: {c1['name']} vs {c2['name']}")
    print(f"Indicator:  {indicator_name}")
    print("="*75)
    
    if indicator_name == "Capital City":
        cap1 = c1['capitalCity'] if c1['capitalCity'] else 'N/A'
        cap2 = c2['capitalCity'] if c2['capitalCity'] else 'N/A'
        print(f"{'Country':<25} | {'Capital City':<25}")
        print("-" * 55)
        print(f"{c1['name'][:25]:<25} | {cap1:<25}")
        print(f"{c2['name'][:25]:<25} | {cap2:<25}")
    else:
        name1 = f"{c1['name'][:25]:<25}"
        name2 = f"{c2['name'][:25]:<25}"
        print(f"{'Year':<10} | {name1} | {name2}")
        print("-" * 75)
        
        for i in range(5):
            if i >= len(data1) and i >= len(data2):
                break
            v1 = data1[i]['value'] if i < len(data1) and data1[i]['value'] is not None else 0
            v2 = data2[i]['value'] if i < len(data2) and data2[i]['value'] is not None else 0
            y1 = data1[i]['date'] if i < len(data1) else "-"
            y2 = data2[i]['date'] if i < len(data2) else "-"
            year = y1 if y1 != "-" else y2
            val1_str = f"{v1:,.2f}" if v1 != 0 else "-"
            val2_str = f"{v2:,.2f}" if v2 != 0 else "-"
            print(f"{year:<10} | {val1_str:<25} | {val2_str:<25}")
    print("="*75)

def main():
    clear_screen()
    print("Initializing Country Development Explorer...")
    countries_db = fetch_all_countries()
    
    if not countries_db:
        print("Failed to load initial data.")
        return

    while True:
        print("\n=== Country Development Explorer ===")
        print("World Bank Open Data API (No API key required)")
        print("\n1. Search for a country")
        print("2. Compare two countries")
        print("3. Exit")
        
        choice = input("\nSelect an option (1-3): ").strip()
        
        if choice == "1":
            print("\nAvailable Indicators:")
            for key, (name, code) in INDICATORS.items():
                print(f"{key}. {name}")
                
            ind_choice = input("\nChoose an indicator (1-5): ").strip()
            if ind_choice not in INDICATORS:
                print("Invalid indicator choice.")
                continue
                
            ind_name, ind_code = INDICATORS[ind_choice]
            
            country_name = input("\nEnter country name or code (e.g. Rwanda or RW): ").strip()
            country_info = get_country_info(countries_db, country_name)
            
            if not country_info:
                print(f"\nError: Country '{country_name}' not found.")
                input("Press Enter to continue...")
                continue
                
            print(f"\nFetching data for {country_info['name']}...")
            
            if ind_code == "CAPITAL_CITY":
                display_country_data(country_info, None, ind_name)
            else:
                indicator_data = fetch_indicator_data(country_info['id'], ind_code)
                if not indicator_data:
                    print("No data available for this selection.")
                else:
                    display_country_data(country_info, indicator_data, ind_name)
            
            input("\nPress Enter to return to menu...")
            clear_screen()
            
        elif choice == "2":
            print("\nAvailable Indicators:")
            for key, (name, code) in INDICATORS.items():
                print(f"{key}. {name}")
                
            ind_choice = input("\nChoose an indicator (1-5): ").strip()
            if ind_choice not in INDICATORS:
                print("Invalid indicator choice.")
                continue
                
            ind_name, ind_code = INDICATORS[ind_choice]
            
            c1_name = input("\nEnter First country name/code: ").strip()
            c1 = get_country_info(countries_db, c1_name)
            
            c2_name = input("Enter Second country name/code: ").strip()
            c2 = get_country_info(countries_db, c2_name)
            
            if not c1 or not c2:
                print("\nError: One or both countries not found.")
                input("Press Enter to continue...")
                continue
                
            print(f"\nFetching comparison data...")
            
            if ind_code == "CAPITAL_CITY":
                display_compare(c1, c2, [], [], ind_name)
            else:
                d1 = fetch_indicator_data(c1['id'], ind_code)
                d2 = fetch_indicator_data(c2['id'], ind_code)
                if not d1 and not d2:
                    print("No data available.")
                else:
                    display_compare(c1, c2, d1 or [], d2 or [], ind_name)
                
            input("\nPress Enter to return to menu...")
            clear_screen()

        elif choice == "3":
            print("\nGoodbye.")
            break
        else:
            print("Invalid choice.")
            input("Press Enter to continue...")
            clear_screen()

if __name__ == "__main__":
    main()
