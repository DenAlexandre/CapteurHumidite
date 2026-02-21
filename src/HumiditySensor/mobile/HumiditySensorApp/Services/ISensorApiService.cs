using HumiditySensorApp.Models;

namespace HumiditySensorApp.Services;

public interface ISensorApiService
{
    Task<HumidityReading> GetHumidityAsync();
    Task<AppConfig> GetConfigAsync();
    Task<List<SensorDataPoint>> GetSensorDataAsync(DateTime start, DateTime end);
    Task SetConfigAsync(string field, string value);
    Task SetRelayAsync(bool on);
    Task RebootAsync();
}
