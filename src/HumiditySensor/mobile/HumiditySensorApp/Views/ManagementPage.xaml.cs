using HumiditySensorApp.ViewModels;

namespace HumiditySensorApp.Views;

public partial class ManagementPage : ContentPage
{
    private readonly ManagementViewModel _vm;
    private bool _manualModeChanging;
    private bool _ventilationChanging;

    public ManagementPage(ManagementViewModel vm)
    {
        InitializeComponent();
        BindingContext = _vm = vm;
    }

    protected override async void OnAppearing()
    {
        base.OnAppearing();
        _vm.PropertyChanged += OnViewModelPropertyChanged;
        await _vm.LoadConfigCommand.ExecuteAsync(null);
    }

    protected override void OnDisappearing()
    {
        base.OnDisappearing();
        _vm.PropertyChanged -= OnViewModelPropertyChanged;
    }

    private async void OnViewModelPropertyChanged(object? sender, System.ComponentModel.PropertyChangedEventArgs e)
    {
        switch (e.PropertyName)
        {
            case nameof(ManagementViewModel.IsManualMode) when !_manualModeChanging:
                _manualModeChanging = true;
                await _vm.ToggleManualModeCommand.ExecuteAsync(null);
                _manualModeChanging = false;
                break;
            case nameof(ManagementViewModel.IsVentilationOn) when !_ventilationChanging:
                _ventilationChanging = true;
                await _vm.ToggleVentilationCommand.ExecuteAsync(null);
                _ventilationChanging = false;
                break;
        }
    }
}
