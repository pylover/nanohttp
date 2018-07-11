from nanohttp import Controller, RestController, context, html, json, HTTPFound


class TipsControllers(RestController):
    @json
    def get(self, tip_id: int = None):
        if tip_id is None:
            return [dict(id=i, title="Tip %s" % i) for i in range(1, 4)]
        else:
            return dict(
                id=tip_id,
                title="Tip %s" % tip_id
            )

    @json
    def post(self, tip_id: int = None):
        tip_title = context.form.get('title')
        print(tip_id, tip_title)

        # Updating the tips title
        # TipStore.get(tip_id).update(tip_title)
        raise HTTPFound('/tips/')


class Root(Controller):
    tips = TipsControllers()

    @html
    def index(self):
        yield """
        <html><head><title>nanohttp Demo</title></head><body>
        <form method="POST" action="/tips/2">
            <input type="text" name="title" />
            <input type="submit" value="Update" />
        </form>
        </body></html>
        """
