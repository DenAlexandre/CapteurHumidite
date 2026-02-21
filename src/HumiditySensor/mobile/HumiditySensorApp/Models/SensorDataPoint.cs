namespace HumiditySensorApp.Models;

public class SensorDataPoint
{
    public DateTime DateTime { get; set; }
    public double Temperature { get; set; }
    public double Humidity { get; set; }
    public bool Output { get; set; }
}
