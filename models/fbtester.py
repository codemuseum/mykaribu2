import facebook

class FbTester:
    @staticmethod
    def WallPost(access_token, message):
        attach = {
            "name": "This is only a test",
            "link": "http://www.example.com/",
            "caption": "{*actor*} posted a new test",
            "description": "And here's something longer",
            "picture": "http://icanhascheezburger.files.wordpress.com/2010/06/funny-pictures-cat-makes-rude-gesture.jpg"}

        graph = facebook.GraphAPI(access_token)
        graph.put_wall_post(message=message, attachment=attach)