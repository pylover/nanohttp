from nanohttp import Controller, RestController, context, html, json, \
    HTTPFound


tips = [
    dict(id=i, title="Tip %s" % i) for i in range(1, 4)
]


class TipsControllers(RestController):
    @json
    def get(self, tip_id: int = None):
        if tip_id is None:
            return tips

        for tip in tips:
            if tip['id'] == int(tip_id):
                return tip

        raise HTTPNotFound(f'Tip: {tip_id} is not found')

    @json(prevent_empty_form=True)
    def post(self):
        tip_title = context.form.get('title')
        # Updating the tips global variable
        tip_id = len(tips)+1
        tips.append(dict(id=tip_id, title=tip_title))
        raise HTTPFound('/tips/')


class Root(Controller):
    tips = TipsControllers()

    @html(prevent_form='400 Form Not Allowed')
    def index(self):
        yield """
        <html><head><title>nanohttp Demo</title></head><body>
        <form method="POST" action="/tips/">
            <input type="text" name="title" />
            <input type="submit" value="Update" />
        </form>
        </body></html>
        """

