from flask_restx import Resource

from src.api.nsmodels import events_ns, events_model
from src.models import SeismicEvent

@events_ns.route('/events')
@events_ns.doc(responses={200: 'OK', 400: 'Invalid Argument', 401: 'JWT Token Expires', 403: 'Unauthorized', 404: 'Not Found'})
class SeismicListAPI(Resource):
    @events_ns.marshal_list_with(events_model)
    def get(self):
        """List all seismic events"""
        events = SeismicEvent.query.all()
        if not events:
            return {"error": "მიწისძვრები არ მოიძებნა."}, 404

        return events