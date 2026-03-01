using System.Globalization;
using System.Text;
using System.Text.Json;
using HumiditySensorApp.Models;

namespace HumiditySensorApp.Services;

public class SensorApiService : ISensorApiService
{
    private readonly HttpClient _http;
    private readonly IApiSettingsService _settings;

    public SensorApiService(HttpClient http, IApiSettingsService settings)
    {
        _http = http;
        _settings = settings;
    }

    private string Url(string path) => $"{_settings.BaseUrl}{path}";

    public async Task<HumidityReading> GetHumidityAsync()
    {
        var response = await _http.GetAsync(Url("/get_humidity"));
        response.EnsureSuccessStatusCode();
        var json = await response.Content.ReadAsStringAsync();
        using var doc = JsonDocument.Parse(json);
        var root = doc.RootElement;

        return new HumidityReading
        {
            Temperature = root.GetProperty("temperature").GetDouble(),
            Humidity = root.GetProperty("humidity").GetDouble()
        };
    }

    public async Task<AppConfig> GetConfigAsync()
    {
        var response = await _http.GetAsync(Url("/get_config"));
        response.EnsureSuccessStatusCode();
        var json = await response.Content.ReadAsStringAsync();
        using var doc = JsonDocument.Parse(json);
        var rows = doc.RootElement.GetProperty("reponse");

        var config = new AppConfig();
        foreach (var row in rows.EnumerateArray())
        {
            var field = row[1].GetString();
            var value = row[2].GetString();
            switch (field)
            {
                case "cons_hum":
                    if (int.TryParse(value, out var setpoint))
                        config.Setpoint = setpoint;
                    break;
                case "mode_manual":
                    config.IsManualMode = value == "1";
                    break;
            }
        }
        return config;
    }

    public async Task<List<SensorDataPoint>> GetSensorDataAsync(DateTime start, DateTime end)
    {
        var body = JsonSerializer.Serialize(new
        {
            datetime_start = start.ToString("yyyy-MM-dd HH:mm:ss"),
            datetime_end = end.ToString("yyyy-MM-dd HH:mm:ss")
        });
        var content = new StringContent(body, Encoding.UTF8, "application/json");
        var response = await _http.PostAsync(Url("/get_sensors_data"), content);
        response.EnsureSuccessStatusCode();
        var json = await response.Content.ReadAsStringAsync();
        using var doc = JsonDocument.Parse(json);
        var reponse = doc.RootElement.GetProperty("reponse");

        var result = new List<SensorDataPoint>();

        if (reponse.GetArrayLength() < 2)
            return result;

        var dataArray = reponse[1];
        foreach (var row in dataArray.EnumerateArray())
        {
            var dtStr = row[1].GetString();
            var temp = row[2].GetDouble();
            var hum = row[3].GetDouble();
            var outputStr = row[4].ToString();

            var point = new SensorDataPoint
            {
                Temperature = temp,
                Humidity = hum,
                Output = string.Equals(outputStr, "True", StringComparison.OrdinalIgnoreCase)
            };

            if (DateTime.TryParse(dtStr, CultureInfo.InvariantCulture, DateTimeStyles.None, out var dt))
                point.DateTime = dt;

            result.Add(point);
        }

        return result;
    }

    public async Task SetConfigAsync(string field, string value)
    {
        var body = JsonSerializer.Serialize(new { field, value });
        var content = new StringContent(body, Encoding.UTF8, "application/json");
        var response = await _http.PostAsync(Url("/set_config"), content);
        response.EnsureSuccessStatusCode();
    }

    public async Task SetRelayAsync(bool on)
    {
        var body = JsonSerializer.Serialize(new { output = on ? "true" : "false" });
        var content = new StringContent(body, Encoding.UTF8, "application/json");
        var response = await _http.PostAsync(Url("/set_outputRelayPin17"), content);
        response.EnsureSuccessStatusCode();
    }

    public async Task RebootAsync()
    {
        var content = new StringContent("{}", Encoding.UTF8, "application/json");
        try
        {
            await _http.PostAsync(Url("/reboot"), content);
        }
        catch (HttpRequestException) { }
        catch (TaskCanceledException) { }
    }
}
