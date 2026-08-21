import requests

# ඔයා දැන් හොයාගත්ත විස්තර දෙක
page_id = '1351710984681459'
access_token = 'EAAeYCdPhRzYBSbaO9Lcq1A9G0gO4BkKY0pXZAw9UhLxq0IexLZAuKtV1bb7ZCatD79zDHJv24MhWvIsIRvWUsBDcOu8XofZCPOok4oF4qZBbZCS2xii8P0YQjBXiVe6ThEkAF87y73ZAOO7FZCjSi7nu4RuIVpxslH4VkYgV5Ol2GeeQwzRcNwPXhKaUJkrzPuPVLFn6Q4PZAW4VzfaRMLrmeD3XynjNamyM3DZBZCStdBPYixm'

# Facebook Graph API එකේ URL එක
url = f'https://graph.facebook.com/{page_id}/feed'

# පේජ් එකට දාන්න ඕන පෝස්ට් එක
payload = {
    'message': 'Hello everyone! 🚀',
    'access_token': access_token
}

# පෝස්ට් එක Facebook එකට යැවීම
response = requests.post(url, data=payload)

# ප්‍රතිඵලය බැලීම
if response.status_code == 200:
    print("නියමයි! පෝස්ට් එක සාර්ථකව පබ්ලිෂ් වුණා! 🎉")
    print("Post ID:", response.json().get('id'))
else:
    print("පොඩි අවුලක් තියෙනවා 😥")
    print(response.json())