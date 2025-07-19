# Auto Schedule Maker

I really like having all my class times in Google Calendar because it gives me reminders on my phone to go to class.  
Saves my butt all the time because I be forgetting.

**BUTTT** I always hated having to manually put all the classes and their times into Google Calendar — it was very *tedious* in my opinion.  
So my solution to that was this code. It’s a little janky and I can improve it, but it works pretty good for now!

It uses bounding boxes to determine which columns to extract the information from in the JPG I provided.  
It might not work for different types of schedules than the one provided, but I will be improving on that.

---

## Necessary Installation to Run It

1. `pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib`
2. `pip install google-cloud-vision`
3. `pip install pillow`
4. `pip install regex`

### One-Liner for All the Above
```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib google-cloud-vision pillow regex
