export const URL = "http://localhost:8000/oskyapi";
export const routesEndpoint = "api/routes?callsign={callsign}";
export const aircraftEndpoint = "api/metadata/aircraft/icao/{icao24}";
export const airportsEndpoint = "api/airports/?icao={ICAO}";

export class Constants {
  public static DEFAULT_MIN_LATITUDE = -90;
  public static DEFAULT_MAX_LATITUDE = 90;
  public static DEFAULT_MIN_LONGITUDE = -180;
  public static DEFAULT_MAX_LONGITUDE = 180;
}
