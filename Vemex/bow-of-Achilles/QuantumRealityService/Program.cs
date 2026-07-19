using System;
using System.ServiceProcess;
using System.Diagnostics;

namespace RealityBraker
{
    static class Program
    {
        /// <summary>
        /// The main entry point for the application.
        /// </summary>
        static void Main()
        {
            try
            {
                // Create the service
                ServiceBase[] ServicesToRun;
                ServicesToRun = new ServiceBase[]
                {
                    new QuantumRealityService()
                };
                
                // Run the service
                ServiceBase.Run(ServicesToRun);
            }
            catch (Exception ex)
            {
                // Log any startup errors
                EventLog.WriteEntry("QuantumRealityService", "Failed to start service: " + ex.Message, EventLogEntryType.Error);
            }
        }
    }
}