from flask_restx import reqparse, fields
from src.extensions import api


event_ns = api.namespace('Events', description='API endpoint for Seismic event operations', path='/api')

# RESTX model for Swagger
event_model = event_ns.model("SeismicEvent", {
    "id": fields.Integer(readOnly=True),
    "origin_time": fields.DateTime,
    "latitude": fields.Float,
    "longitude": fields.Float,
    "depth": fields.Float,
    "region_en": fields.String,
    "area": fields.String,
    "station_record_count": fields.Integer,
    "phases_count": fields.Integer,
    "intensity": fields.Float,
    "info_en": fields.String,
    "important": fields.String,
})

event_parser = reqparse.RequestParser()
event_parser.add_argument("origin_time", type=str, required=True, help="Origin time is required (ISO 8601)")
event_parser.add_argument("latitude", type=float, required=True, help="Latitude is required")
event_parser.add_argument("longitude", type=float, required=True, help="Longitude is required")
event_parser.add_argument("depth", type=float, required=True, help="Depth is required")
event_parser.add_argument("region_en", type=str, required=True, help="Region is required")
event_parser.add_argument("area", type=str, required=False)
event_parser.add_argument("station_record_count", type=int, required=False, default=0)
event_parser.add_argument("phases_count", type=int, required=False, default=0)
event_parser.add_argument("intensity", type=float, required=False)
event_parser.add_argument("info_en", type=str, required=False)
event_parser.add_argument("important", type=str, required=False)
