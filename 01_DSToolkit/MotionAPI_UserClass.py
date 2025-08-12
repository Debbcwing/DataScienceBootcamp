import requests
import json

class User:
    def __init__(self,email,password):
        url = "/api/auth/token/"
        resp = requests.post("https://motion.propulsion-home.ch/backend" + url,data={"email": email, "password": password},)
        if resp.status_code < 400:
            login_data= resp.json()
            self.login_data = login_data
            self.token = resp.json()['access'] 
            self.base_url = "https://motion.propulsion-home.ch/backend"
            self.headers = {"Authorization": f"Bearer {self.token}",}
        else:
            print('invalid email / password')

    def getcurrentuser(self):
        url = self.base_url + "/api/users/me"
        resp = requests.get(url,headers=self.headers )
        print(resp.json())

    # lists all users on motion API
    def listallusers(self):
        url = self.base_url + "/api/users/"
        while True:
            list_of_users = requests.get(url,headers=self.headers)
            dict_of_users = json.loads(list_of_users.text)
            print('Motion API has the following users:')
            for i in range(len(dict_of_users['results'])):
                firstname = dict_of_users['results'][i]['first_name']
                lastname = dict_of_users['results'][i]['last_name']
                id = dict_of_users['results'][i]['id']
                email = dict_of_users['results'][i]['email']
                print(f'{firstname} {lastname} has the email-address {email} and the id {id}')
            print('Input what you want to do')
            print('Show next side: n, show previous side: p, exit: e')
            order = input()
            if order == 'n':
                if dict_of_users['next'] != None:
                    url = dict_of_users['next']
                else:
                    print('There is no next site')
            elif order == 'p':
                if dict_of_users['previous'] != None:
                    url = dict_of_users['previous']
                else:
                    print('There is no previous site')
            elif order == 'e':
                break
            else:
                print('This isnt a valid input')

    # sending a friend request to the user with the id = friend_id
    def sendfriendrequest(self,friend_id):
        url = "/api/social/friends/request/"+str(friend_id)+"/"
        friendrequest = requests.post(self.base_url + url,headers=self.headers)
        if friendrequest.status_code < 400:
            print(f"Succesfully sent a friendrequest to user {friend_id}")
        elif friendrequest.status_code == 403:
            print(f"User {friend_id} already has a friend request from you")
        else:
            print(f"Something went wrong when trying to send a friend request to user {friend_id}, idk what but heres the result: {friendrequest.content}")

    # print a list of all pending friend requests
    def checkoutfriendrequests(self):
        url = "/api/social/friends/requests/"
        list_of_friendrequest = requests.get(self.base_url + url ,headers = self.headers)
        dict_of_friendrequest = json.loads(list_of_friendrequest.text)
        if dict_of_friendrequest['count'] == 0:
            print('You have no friend requests')
        else:
            for i in range(len(dict_of_friendrequest['results'])):
                receiver_name = dict_of_friendrequest['results'][i]['receiver']['first_name'] + ' ' + dict_of_friendrequest['results'][i]['receiver']['last_name']
                requester_name = dict_of_friendrequest['results'][i]['requester']['first_name'] + ' ' + dict_of_friendrequest['results'][i]['requester']['last_name']
                print(f'There is a friend request from {requester_name} to {receiver_name}')
            
    # get all pending friend requests where you are the receiver
    def checkoutpendingfriendrequests(self):
        list_of_pending_friendrequests = []
        url = "/api/social/friends/requests/"
        list_of_friendrequest = requests.get(self.base_url + url ,headers={"Authorization": f"Bearer {self.token}",},)
        dict_of_friendrequest = json.loads(list_of_friendrequest.text)
        for i in range(len(dict_of_friendrequest['results'])):
            if dict_of_friendrequest['results'][i]['status'] == 'P':
            #if dict_of_friendrequest['results'][i]['receiver']['id'] == self.login_data['user']['id'] and dict_of_friendrequest['results'][i]['status'] == 'P':
                list_of_pending_friendrequests.append(dict_of_friendrequest['results'][i])
        if(len(list_of_pending_friendrequests) == 0):
            print('There are no pending friend requests to you right now')
        else:
            print("There are the following pending friend requests:")
            for i in range(len(list_of_pending_friendrequests)):
                receiver_name = str(list_of_pending_friendrequests[i]['receiver']['id']) + ' ' + list_of_pending_friendrequests[i]['receiver']['first_name'] + ' '+ list_of_pending_friendrequests[i]['receiver']['last_name']
                requester_name = str(list_of_pending_friendrequests[i]['requester']['id']) + ' ' + list_of_pending_friendrequests[i]['requester']['first_name'] + ' ' + list_of_pending_friendrequests[i]['requester']['last_name']
                print(f'from {requester_name} to {receiver_name}')
        return list_of_pending_friendrequests

    # accept all pending friend requests where you are the receiver
    def acceptallfriendrequests(self):
        list_of_friend_requests = self.checkoutpendingfriendrequests()
        for i in range(len(list_of_friend_requests)):
            data = list_of_friend_requests[i]
            url = "/api/social/friends/requests/"+str(data['id'])+"/"
            data['status'] = 'A'
            result = requests.patch(self.base_url + url ,headers={"Authorization": f"Bearer {self.token}",},data = data)
            receiver_name = str(data['receiver']['id']) + ' ' + data['receiver']['first_name'] + ' '+ data['receiver']['last_name']
            requester_name = str(data['requester']['id']) + ' ' + data['requester']['first_name'] + ' ' + data['requester']['last_name']
            if result.status_code < 400:
                print(f'Accepted friend request from {requester_name} to {receiver_name}')
            else:
                print(f"Something went wrong when trying to accept the friend request from {requester_name} to {receiver_name}.")
                print(result.content)

    # post the string message
    def postmessage(self,message):
        url = "/api/social/posts/"
        requests.post(self.base_url + url,headers={"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"},data = json.dumps({"content" : message}),)

    # prints all posts from all friends
    def printallfriendposts(self):
        url = "/api/social/friends/"
        list_of_friends = requests.get(self.base_url + url ,headers={"Authorization": f"Bearer {self.token}",},)
        dict_of_friends = json.loads(list_of_friends.text)
        friend_ids = []
        friend_posts= [[],[]]
        for i in range(len(dict_of_friends['results'])):
            friend_id = dict_of_friends['results'][i]['id']
            friend_ids.append(friend_id)
        #print('friend_ids: '+str(friend_ids))
        url = self.base_url + "/api/social/posts/"
        while True:
            list_of_all_posts = requests.get(url ,headers={"Authorization": f"Bearer {self.token}",},)
            dict_of_all_posts = json.loads(list_of_all_posts.text)
            for i in range(len(dict_of_all_posts['results'])):
                if dict_of_all_posts['results'][i]['user']['id'] in friend_ids:
                    name = dict_of_all_posts['results'][i]['user']['first_name'] + ' ' +  dict_of_all_posts['results'][i]['user']['last_name']
                    post = dict_of_all_posts['results'][i]['content']
                    friend_posts[0].append(name)
                    friend_posts[1].append(post)
            if dict_of_all_posts['next'] != None:
                url = dict_of_all_posts['next']
            else:
                break
        #print(friend_posts)
        for i in range(len(friend_posts[0])):
            name = friend_posts[0][i]
            post = friend_posts[1][i]
            print(f'{name} posted {post}')

    # prints all posts ever posted
    def printallposts(self):
        url = self.base_url + "/api/social/posts/"
        while True:
            list_of_all_posts = requests.get(url ,headers={"Authorization": f"Bearer {self.token}",},)
            dict_of_all_posts = json.loads(list_of_all_posts.text)
            for i in range(len(dict_of_all_posts['results'])):
                name = dict_of_all_posts['results'][i]['user']['first_name'] + ' ' +  dict_of_all_posts['results'][i]['user']['last_name']
                post = dict_of_all_posts['results'][i]['content']
                print(f'{name} posted {post}')
            print('Input what you want to do')
            print('Show next side: n, show previous side: p, exit: e')
            order = input()
            if order == 'n':
                if dict_of_all_posts['next'] != None:
                    url = dict_of_all_posts['next']
                else:
                    print('There is no next site')
            elif order == 'p':
                if dict_of_all_posts['previous'] != None:
                    url = dict_of_all_posts['previous']
                else:
                    print('There is no previous site')
            elif order == 'e':
                break
            else:
                print('This isnt a valid input')

    # changes the first name
    def changefirstname(self,new_first_name):
        url = "/api/users/me/"
        data = self.login_data['user']
        data['first_name'] = new_first_name
        requests.patch(self.base_url + url ,headers={"Authorization": f"Bearer {self.token}",},data = data)

    # changes the last name
    def changelastname(self,new_last_name):
        url = "/api/users/me/"
        data = self.login_data['user']
        data['last_name'] = new_last_name
        requests.patch(self.base_url + url ,headers={"Authorization": f"Bearer {self.token}",},data = data)