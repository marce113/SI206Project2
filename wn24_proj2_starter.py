from bs4 import BeautifulSoup
import re
import os
import csv
import unittest

# Marcela Passos and CarolinaJanicke
# Used Chat GPT to help debug and make functions more effecient

# IMPORTANT NOTE:
"""
If you are getting "encoding errors" while trying to open, read, or write from a file, add the following argument to any of your open() functions:
    encoding="utf-8-sig"

An example of that within the function would be:
    open("filename", "r", encoding="utf-8-sig")

There are a few special characters present from Airbnb that aren't defined in standard UTF-8 (which is what Python runs by default). This is beyond the scope of what you have learned so far in this class, so we have provided this for you just in case it happens to you. Good luck!
"""

def retrieve_listings(html_file): 
    """
    retrieve_listings(html_file) -> list 

    TODO Write a function that takes file data from the variable html_file, reads it, and loads it into a BeautifulSoup object 

    Parse through the object, and return a list of tuples that includes the listing title and the listing id. 
        
        The listing id is found in the url of a listing. For example, for https://www.airbnb.com/rooms/1944564 the listing id is 1944564.

    Example output: 
        [('Loft in Mission District', '1944564'), ('Home in Mission District', '49043049'), ...]

    """
    with open(html_file, 'r', encoding="utf-8-sig") as file: 
        html_data = file.read()

    soup = BeautifulSoup(html_data, 'html.parser')
    listings = soup.find_all('div', class_='t1jojoys dir dir-ltr')
    listing_list = []
    for listings in listings:
            title = listings.get_text()
            listing_id = re.search(r'id="title_(\d+)', str(listings)).group(1)
            listing_list.append((title, listing_id))
  
    return listing_list

def listing_details(listing_id): 
    """
    listing_details(listing_id) -> tuple

    TODO Write a function that takes a string containing the listing id of an Airbnb and returns a tuple that includes the policy number, the host name(s), the place type, the average review score, and the nightly price of the listing. 

        Policy number (data type: str) - either a string of the policy number, "Pending", or "Exempt". 
            This field can be found in the section about the host.
            Note that this is a text field the lister enters, this could be a policy number, or the word "Pending" or "Exempt" or many others. Look at the raw data, decide how to categorize them into the three categories.

        Host name(s) (data type: str) - either the host name or  "missing". 
            Beware some listings have multiple hosts– please make sure to capture both names (e.g. "Seth And Alexa")


        Place type (data type: str) - either "Entire Room", "Private Room", or "Shared Room"
            Note that this data field is not explicitly given from this page. Use the following to categorize the data into these three fields.
                "Private Room": the listing subtitle has the word "private" in it
                "Shared Room": the listing subtitle has the word "shared" in it
                "Entire Room": the listing subtitle has neither the word "private" nor "shared" in it

        Average Review Score (data type: float)
            Do not forget to account for listings which have no reviews 

        Nightly price of listing (data type: int)

    Example output: 
        ('2022-004088STR', 'Brian', 'Entire Room', 4.98, 181)

    """
    with open(f"html_files/listing_{listing_id}.html", 'r', encoding="utf-8-sig") as file:
        soup = BeautifulSoup(file, 'html.parser')
        
        # get policy number
        policy_number = "Exempt"
        policy_element = soup.find('li', class_='f19phm7j')
        if policy_element:
            policy_number = policy_element.get_text(strip=True).split(":")[-1].strip()

        #get host name
        host_name = 'missing'
        subtitle = soup.find('h2', class_='_14i3z6h')
        if subtitle:
            host_name = subtitle.get_text(strip=True).split("hosted by")[-1].strip()
            if not host_name:
                host_name = 'missing'        
        
        #get place type
        place_type = "Entire Room"
        # Extract the room type from subtitle
        if "private" in subtitle:
            place_type = "Private Room"
        elif "shared" in subtitle:
            place_type = "Shared Room"
        
        #get review score
        review_score = 0.0
        review_element = soup.find('span', class_='_17p6nbba')
        if review_element:
            review_text = review_element.get_text(strip=True)[:4]
            if review_text:
                review_score = float(review_text)
        
        #get price per night
        nightly_price = 0
        prices = soup.find_all('span', class_='a8jt5op')
        for price in prices:
            price_text = price.get_text(strip=True)
            if '$' in price_text:
                nightly_price = int(price_text[1:5])
                break

        return (policy_number, host_name, place_type, review_score, nightly_price)


def make_listing_database(html_file): 
    """
    make_listing_database(html_file) -> list

    TODO Write a function that takes in a variable representing the path of the search_results.html file then calls the functions retrieve_listings() and listing_details() in order to create and return the complete listing information. 
    
    This function will use retrieve_listings() to create an initial list of Airbnb listings. Then use listing_details() to obtain additional information about the listing to create a complete listing, and return this information in the structure: 

        [
        (Listing Title 1,Listing ID 1,Policy Number 1, Host Name(s) 1, Place Type 1, Average Review Score 1, Nightly Rate 1),
        (Listing Title 2,Listing ID 2,Policy Number 2, Host Name(s) 2, Place Type 2, Average Review Score 2, Nightly Rate 2), 
        ... 
        ]

    NOTE: retrieve_listings() returns a list of tuples where the tuples are of length 2, listing_details() returns just a tuple of length 5, and THIS FUNCTION returns a list of tuples where the tuples are of length 7. 

    Example output: 
        [('Loft in Mission District', '1944564', '2022-004088STR', 'Brian', 'Entire Room', 4.98, 181), ('Home in Mission District', '49043049', 'Cherry', 'Pending', 'Entire Room', 4.93, 147), ...]    
    """
     #Make a list from retrieve_listing of the basic listing info
    basic_listings = retrieve_listings(html_file)

    # Retrieve detailed information for each listing and combine them
    complete_listing_list = []
    for title, listing_id in basic_listings:
        policy_number, host_name, place_type, average_review_score, nightly_price = listing_details(listing_id)
        All_info = (title, listing_id, policy_number, host_name, place_type, average_review_score, nightly_price)
        complete_listing_list.append(All_info)

    return complete_listing_list
   



def write_csv(data, filename): 
    """
    TODO Write a function that takes in a list of tuples called data, (i.e. the one that is returned by make_listing_database()), sorts the tuples in ascending order by average review score, writes the data to a csv file, and saves it to the passed filename. 
    
    The first row of the csv should contain "Listing Title", "Listing ID", "Policy Number", "Host Name(s)", "Place Type", "Average Review Score", "Nightly Rate", respectively as column headers. 
    
    For each tuple in the data, write a new row to the csv, placing each element of the tuple in the correct column. The data should be written in the csv in ascending order by average review score.

    Example output in csv file: 
        Listing Title,Listing ID,Policy Number,Host Name(s),Place Type,Average Review Score,Nightly Rate
        Apartment in Noe Valley,824047084487341932,2022-008652STR,Eileen,Entire Room,0.0,176
        Home in Mission District,11442567,STR-0005421,Bernat,Entire Room,4.79,164
        ...


    """
   # Sort the data in ascending order by average review score
    sorted_data = sorted(data, key = lambda x: x[5])    # lambda is the function to get the average review score from the 5th index in each tuple
    

    with open(filename, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        
        # Write the header row
        header = ["Listing Title", "Listing ID", "Policy Number", "Host Name(s)", "Place Type", "Average Review Score", "Nightly Rate"]
        writer.writerow(header)
        
        # Write each tuple in sorted_data to the CSV
        for row in sorted_data:
            writer.writerow(row)

def find_invalid_policy_numbers(data):
    """
    find_invalid_policy_numbers(data) -> list

    TODO Write a function that takes in a list of tuples called data, (i.e. the one that is returned by make_listing_database()), and parses through the policy number of each, validating that the policy number matches the policy number format. Ignore any pending or exempt listings. 

    Return a list of tuples that contains the listing id, host name(s), and invalid policy number for listings whose respective policy numbers that do not match the correct format.
        
        Policy numbers are a reference to the business license San Francisco requires to operate a short-term rental. These come in two forms below. # means any digit 0-9.

            20##-00####STR
            STR-000####

    Example output: 
    [('1944564', 'Brian', '2022-004088STR'), ...]

    """
    invalid_policy_numbers = []

    # Regular expression pattern to match valid policy numbers
    valid_pattern = re.compile(r'^(20\d{2}-00\d{4}STR|STR-000\d{4})$')

    for listing_id, _, policy_number, host_names, _, _, _ in data:
        # Skip over any "Pending" or "Exempt" policy numbers
        if policy_number in ["Pending", "Exempt"]:
            continue

        # Check if the policy number matches the valid pattern
        if not valid_pattern.match(policy_number):
            # If it doesn't match, add it to the list of invalid policy numbers
            invalid_policy_numbers.append((listing_id, host_names, policy_number))

# EXTRA CREDIT 
def goodreads_searcher(query): 
    """
    goodreads_searcher(query) -> list

    TODO Write a function that imports requests library of Python
    and sends a request to good reads with the passed query.
    
    Using BeautifulSoup, find all titles and return the list of titles you see on page 1. 
    (that means, you do not need to scrape results on other pages)

    You do not need to write test cases for this question.

    Example output using 'airbnb' as query: 
        ['The Upstarts: How Uber, Airbnb, and the Killer Companies of the New Silicon Valley Are Changing the World', 
        'The Airbnb Story: How Three Ordinary Guys Disrupted an Industry, Made Billions . . . and Created Plenty of Controversy', 
        'Extreme Teams: Why Pixar, Netflix, Airbnb, and Other Cutting-Edge Companies Succeed Where Most Fail', 
        'Optimize YOUR Bnb: The Definitive Guide to Ranking #1 in Airbnb Search by a Prior Employee', 
        'How to Start a Successful Airbnb Business: Quit Your Day Job and Earn Full-time Income on Autopilot With a 
         Profitable Airbnb Business Even if You’re an Absolute Beginner (2023)', 
        "You, Me, and Airbnb: The Savvy Couple's Guide to Turning Midterm Rentals into Big-Time Profits", 
        'Get Paid For Your Pad: How to Maximize Profit From Your Airbnb Listing', 
        'How To Invest in Airbnb Properties: Create Wealth and Passive Income Through Smart Vacation Rentals Investing', 
        'Airbnb Listing Hacks - The Complete Guide To Maximizing Your Bookings And Profits', 
        'Work From Home: 50 Ways to Make Money Online Analyzed']



    * see PDF instructions for more details
    """
    pass

# TODO: Don't forget to write your test cases! 
class TestCases(unittest.TestCase):
    def setUp(self):
        self.listings = retrieve_listings("html_files/search_results.html")

    def test_retrieve_listings(self):
        with open("html_files/search_results.html", "r") as file:
            self.html_content = file.read()
        # call retrieve_listings("html_files/search_results.html")
        # and save to a local variable

         # check that the number of listings extracted is correct (18 listings)
        self.assertEqual(len(self.listings), 18)

        # check that the variable you saved after calling the function is a list
        self.assertEqual(type(self.listings), list)

        # check that each item in the list is a tuple
        self.assertTrue(all(isinstance(item, tuple) for item in self.listings))
        # check that the first title and listings id tuple is correct (open the search results html and find it)
        first_listing = self.listings[0]
        self.assertEqual(first_listing, ("Loft in Mission District", "1944564"))

        # check that the last title and listings id tuple is correct (open the search results html and find it)
        last_listing = self.listings[-1]
        self.assertEqual(last_listing, ("Guest suite in Mission District", "467507"))

    def test_listing_details(self):
        html_list = ["467507",
                     "1550913",
                     "1944564",
                     "4614763",
                     "6092596"]
        
        # call listing_details for i in html_list:
        listing_information = [listing_details(id) for id in html_list]

        # check that the number of listings information is correct (5)
        self.assertEqual(len(listing_information), 5)
        for info in listing_information:
            # check that each item in the list is a tuple
            self.assertEqual(type(info), tuple)
            # check that each tuple has 5 elements
            self.assertEqual(len(info), 5)
            # check that the first three elements in the tuple are string
            self.assertEqual(type(info[0]), str)
            self.assertEqual(type(info[1]), str)
            self.assertEqual(type(info[2]), str)
            # check that the fourth element in the tuple is a float
            self.assertEqual(type(info[3]), float)
            # check that the fifth element in the tuple is an int
            self.assertEqual(type(info[4]), int)

        # check that the first listings in the html_list has the correct policy number

        # check that the last listings in the html_list has the correct place type

        # check that the third listings has the correct cost
        

    def test_make_listing_database(self):
        # call make_listing_database on "html_files/search_results.html"
        # and save it to a variable
        detailed_data = make_listing_database("html_files/search_results.html")

        # check that we have the right number of listings (18)
        self.assertEqual(len(detailed_data), 18)
        for i in detailed_data:
            # assert each item in the list of listings is a tuple
                self.assertEqual(type(i), tuple)
            # check that each tuple has a length of 7
                self.assertEqual(len(i), 7)

        # check that the first tuple is made up of the following:
        # ('Loft in Mission District', '1944564', '2022-004088STR', 'Brian', 'Entire Room', 4.98, 181)
        self.assertEqual(detailed_data[0], ('Loft in Mission District', '1944564', '2022-004088STR', 'Brian', 'Entire Room', 4.98, 181))
        # check that the last tuple is made up of the following:
        # ('Guest suite in Mission District', '467507', 'STR-0005349', 'Jennifer', 'Entire Room', 4.95, 165)
        self.assertEqual(detailed_data[-1], ('Guest suite in Mission District', '467507', 'STR-0005349', 'Jennifer', 'Entire Room', 4.95, 165))
        

def test_write_csv(self):
    detailed_data = make_listing_database("html_files/search_results.html")
    write_csv(detailed_data, "test.csv")
    csv_lines = []
    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test.csv'), 'r') as f:
        csv_reader = csv.reader(f)
        for i in csv_reader:
            csv_lines.append(i)

    self.assertEqual(len(csv_lines), 19)

    header_row = csv_lines[0]
    self.assertEqual(header_row, ['Title', 'ID', 'Code', 'Host', 'Room Type', 'Rating', 'Price'])

    second_row = csv_lines[1]
    self.assertEqual(second_row, ['Apartment in Noe Valley', '824047084487341932', '2022-008652STR', 'Eileen', 'Entire Room', '0.0', '176'])

    last_row = csv_lines[-1]
    self.assertEqual(last_row, ['Guest suite in Mission District', '755957132088408739', 'STR-0000315', 'HostWell', 'Entire Room', '5.0', '125'])

    # Redefining csv_lines before the second use
    write_csv(detailed_data, "test.csv")
    csv_lines = []
    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test.csv'), 'r') as f:
        csv_reader = csv.reader(f)
        for i in csv_reader:
            csv_lines.append(i)

    self.assertEqual(len(csv_lines), 19)




    def test_find_invalid_policy_numbers(self):
        # call make_listing_database on "html_files/search_results.html"
        # and save the result to a variable
        detailed_data = make_listing_database("html_files/search_results.html")

        # call find_invalid_policy_numbers on the variable created above and save the result as a variable
        invalid_listings = find_invalid_policy_numbers(detailed_data)

        # check that the return value is a list
        self.assertEqual(type(invalid_listings), list)
        for i in invalid_listings:
            self.assertEqual(type(i), tuple)
            self.assertEqual(len(i), 3)

def main (): 
    detailed_data = make_listing_database("html_files/search_results.html")
    write_csv(detailed_data, "airbnb_dataset.csv")

if __name__ == '__main__':
    main()
    unittest.main(verbosity=2)