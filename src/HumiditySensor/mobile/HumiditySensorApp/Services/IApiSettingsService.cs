namespace HumiditySensorApp.Services;

public interface IApiSettingsService
{
    string BaseUrl { get; }
    void SetBaseUrl(string url);
}
