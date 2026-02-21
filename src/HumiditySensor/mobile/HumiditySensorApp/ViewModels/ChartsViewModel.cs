using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using HumiditySensorApp.Services;
using LiveChartsCore;
using LiveChartsCore.Defaults;
using LiveChartsCore.SkiaSharpView;
using LiveChartsCore.SkiaSharpView.Painting;
using LiveChartsCore.SkiaSharpView.Painting.Effects;
using SkiaSharp;

namespace HumiditySensorApp.ViewModels;

public partial class ChartsViewModel : ObservableObject
{
    private readonly ISensorApiService _api;

    [ObservableProperty]
    private ISeries[] _temperatureSeries = [];

    [ObservableProperty]
    private ISeries[] _humiditySeries = [];

    [ObservableProperty]
    private Axis[] _temperatureYAxes = [new Axis { Name = "°C", MinLimit = 0, MaxLimit = 50 }];

    [ObservableProperty]
    private Axis[] _humidityYAxes = [new Axis { Name = "%", MinLimit = 0, MaxLimit = 100 }];

    [ObservableProperty]
    private Axis[] _xAxes = [new DateTimeAxis(TimeSpan.FromHours(1), d => d.ToString("HH:mm"))];

    [ObservableProperty]
    private string _selectedPeriod = "Aujourd'hui";

    [ObservableProperty]
    private bool _isLoading;

    [ObservableProperty]
    private bool _hasError;

    [ObservableProperty]
    private string _errorMessage = string.Empty;

    [ObservableProperty]
    private bool _isWaiting;

    [ObservableProperty]
    private string _waitingMessage = string.Empty;

    private bool _hasLoadedOnce;

    public List<string> Periods { get; } = ["Aujourd'hui", "24h", "7 jours"];

    public ChartsViewModel(ISensorApiService api)
    {
        _api = api;
    }

    partial void OnSelectedPeriodChanged(string value)
    {
        _ = LoadDataAsync();
    }

    [RelayCommand]
    private async Task LoadDataAsync()
    {
        if (Connectivity.Current.NetworkAccess != NetworkAccess.Internet)
        {
            IsWaiting = !_hasLoadedOnce;
            WaitingMessage = "Pas de connexion réseau";
            HasError = _hasLoadedOnce;
            ErrorMessage = "Pas de connexion réseau";
            return;
        }

        if (!_hasLoadedOnce)
            IsWaiting = true;

        WaitingMessage = "Chargement des données...";
        IsLoading = _hasLoadedOnce;
        HasError = false;

        try
        {
            var now = DateTime.Now;
            var (start, end) = SelectedPeriod switch
            {
                "24h" => (now.AddHours(-24), now),
                "7 jours" => (now.AddDays(-7), now),
                _ => (now.Date, now)
            };

            var data = await _api.GetSensorDataAsync(start, end);

            var tempPoints = data.Select(d => new DateTimePoint(d.DateTime, d.Temperature)).ToList();
            var humPoints = data.Select(d => new DateTimePoint(d.DateTime, d.Humidity)).ToList();

            var config = await _api.GetConfigAsync();
            var setpointPoints = data.Count > 0
                ? new List<DateTimePoint>
                {
                    new(data.First().DateTime, config.Setpoint),
                    new(data.Last().DateTime, config.Setpoint)
                }
                : new List<DateTimePoint>();

            // Adapt X axis to selected period
            var (unit, labelFormat) = SelectedPeriod switch
            {
                "7 jours" => (TimeSpan.FromDays(1), "dd/MM"),
                "24h" => (TimeSpan.FromHours(4), "HH:mm"),
                _ => (TimeSpan.FromHours(1), "HH:mm")
            };

            var xMin = data.Count > 0 ? data.First().DateTime.Ticks : start.Ticks;
            var xMax = data.Count > 0 ? data.Last().DateTime.Ticks : end.Ticks;

            XAxes = [new DateTimeAxis(unit, d => d.ToString(labelFormat))
            {
                MinLimit = xMin,
                MaxLimit = xMax
            }];

            TemperatureSeries =
            [
                new LineSeries<DateTimePoint>
                {
                    Values = tempPoints,
                    Name = "Température",
                    Stroke = new SolidColorPaint(SKColors.OrangeRed, 2),
                    GeometryStroke = null,
                    GeometryFill = null,
                    Fill = null,
                    LineSmoothness = 0.3
                }
            ];

            HumiditySeries =
            [
                new LineSeries<DateTimePoint>
                {
                    Values = humPoints,
                    Name = "Humidité",
                    Stroke = new SolidColorPaint(SKColors.DodgerBlue, 2),
                    GeometryStroke = null,
                    GeometryFill = null,
                    Fill = null,
                    LineSmoothness = 0.3
                },
                new LineSeries<DateTimePoint>
                {
                    Values = setpointPoints,
                    Name = "Consigne",
                    Stroke = new SolidColorPaint(SKColors.Red, 2) { PathEffect = new DashEffect([6f, 4f]) },
                    GeometryStroke = null,
                    GeometryFill = null,
                    Fill = null,
                    LineSmoothness = 0,
                    IsHoverable = false
                }
            ];
            _hasLoadedOnce = true;
            IsWaiting = false;
        }
        catch (Exception ex)
        {
            if (!_hasLoadedOnce)
            {
                IsWaiting = true;
                WaitingMessage = "Serveur indisponible.\nAppuyez pour réessayer.";
            }
            else
            {
                HasError = true;
                ErrorMessage = $"Erreur : {ex.Message}";
            }
        }
        finally
        {
            IsLoading = false;
        }
    }
}
