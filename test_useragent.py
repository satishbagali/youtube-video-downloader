from fake_useragent import UserAgent
import requests

def test_user_agent():
    try:
        # Initialize UserAgent
        ua = UserAgent()
        
        # Print a few different user agents to demonstrate rotation
        print("Testing fake-useragent functionality:\n")
        print("1st User-Agent:", ua.random)
        print("2nd User-Agent:", ua.random)
        print("3rd User-Agent:", ua.random)
        
        # Make a test request to a website using the random user agent
        headers = {'User-Agent': ua.random}
        response = requests.get('https://httpbin.org/user-agent', headers=headers)
        
        print("\nTest request result:")
        print(response.json())
        
        print("\nfake-useragent is working properly!")
        
    except Exception as e:
        print(f"\nError testing fake-useragent: {str(e)}")

if __name__ == "__main__":
    test_user_agent() 