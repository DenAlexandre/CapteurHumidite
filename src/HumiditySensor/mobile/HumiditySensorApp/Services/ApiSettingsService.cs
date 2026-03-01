namespace HumiditySensorApp.Services;

public class ApiSettingsService : IApiSettingsService
{
    private const string BaseUrlKey = "api_base_url";
    private readonly string _defaultUrl;

    public ApiSettingsService(string defaultUrl)
    {
        _defaultUrl = defaultUrl;
    }

    public string BaseUrl
    {
        get => Preferences.Get(BaseUrlKey, _defaultUrl);
    }

    public void SetBaseUrl(string url)
    {
        Preferences.Set(BaseUrlKey, url.TrimEnd('/'));
    }
}
