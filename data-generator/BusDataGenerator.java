
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.Random;

public class BusDataGenerator {

    private static final Random random = new Random(42);

    private static final int RECORDS_PER_ROUTE = 500;

    static class Route {
        String id;
        String busNumber;
        String source;
        String destination;
        int baseMinutes;

        Route(String id, String busNumber, String source,
              String destination, int baseMinutes) {
            this.id = id;
            this.busNumber = busNumber;
            this.source = source;
            this.destination = destination;
            this.baseMinutes = baseMinutes;
        }
    }

    // Candidate routes for the prototype.
    // Verify official route numbers and endpoints before deployment.
    private static final Route[] routes = {
        new Route("R001", "1", "Maruthamalai",
                  "Avarampalayam", 35),
        new Route("R002", "1A", "Ondipudur",
                  "Vadavalli", 50),
        new Route("R003", "2", "Perur",
                  "Polytechnic", 35),
        new Route("R004", "3", "Ganapathy",
                  "Madukkarai", 45),
        new Route("R005", "4", "Thudiyalur",
                  "Podanur", 45),
        new Route("R006", "6A", "Gandhipuram",
                  "Periyanaickanpalayam", 40),
        new Route("R007", "8", "Chettipalayam",
                  "Singanallur", 30),
        new Route("R008", "10", "Saibaba Colony",
                  "Chinniampalayam", 45),
        new Route("R009", "11", "Railway Station",
                  "Kanuvai", 35),
        new Route("R010", "12", "Gandhipuram",
                  "Premier Mills", 30),
        new Route("R011", "12C", "Eachanari",
                  "Polytechnic", 25),
        new Route("R012", "16", "Town Hall",
                  "Airport", 25),
        new Route("R013", "19", "Ukkadam",
                  "Nanjundapuram", 30),
        new Route("R014", "24", "Ukkadam",
                  "Kalapatti", 40),
        new Route("R015", "26", "Ukkadam",
                  "Veerapandipudur", 40),
        new Route("R016", "28", "Gandhipuram",
                  "Thondamuthur", 45),
        new Route("R017", "33F", "Singanallur",
                  "Premier Mills", 25),
        new Route("R018", "52", "Ukkadam",
                  "Saibaba Colony", 25),
        new Route("R019", "55", "Gandhipuram",
                  "Vellalore", 35),
        new Route("R020", "63", "Saravanampatti",
                  "Selvapuram", 40),
        new Route("R021", "70", "Gandhipuram",
                  "Maruthamalai", 40),
        new Route("R022", "95", "Gandhipuram",
                  "Singanallur", 30)
    };

    private static final String[] days = {
        "Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday"
    };

    private static final String[] weatherConditions = {
        "Clear", "Cloudy", "Rain"
    };

    private static final String[] trafficLevels = {
        "Low", "Medium", "High"
    };

    public static void main(String[] args) {
        String fileName = "bus_data.csv";
        String routesFileName = "routes.csv";

        try {
            generateRouteMaster(routesFileName);
            generateTripData(fileName);

            System.out.println("BusWise dataset created successfully!");
            System.out.println("Routes: " + routes.length);
            System.out.println("Trip records: "
                    + (routes.length * RECORDS_PER_ROUTE));
            System.out.println("Files: " + routesFileName
                    + " and " + fileName);

        } catch (IOException e) {
            System.err.println("Error creating CSV files: "
                    + e.getMessage());
        }
    }

    private static void generateRouteMaster(String fileName)
            throws IOException {

        try (PrintWriter writer =
                     new PrintWriter(new FileWriter(fileName))) {

            writer.println(
                "route_id,bus_number,source,destination,base_minutes"
            );

            for (Route route : routes) {
                writer.printf("%s,%s,%s,%s,%d%n",
                    route.id,
                    route.busNumber,
                    route.source,
                    route.destination,
                    route.baseMinutes
                );
            }
        }
    }

    private static void generateTripData(String fileName)
            throws IOException {

        try (PrintWriter writer =
                     new PrintWriter(new FileWriter(fileName))) {

            writer.println(
                "route_id,bus_number,source,destination,day,"
                + "departure_hour,weather,traffic,"
                + "scheduled_minutes,actual_minutes,"
                + "delay_minutes,crowding"
            );

            for (Route route : routes) {
                for (int i = 0; i < RECORDS_PER_ROUTE; i++) {

                    String day = days[random.nextInt(days.length)];
                    int hour = random.nextInt(17) + 6; // 6 AM–10 PM

                    String weather =
                        weatherConditions[
                            random.nextInt(weatherConditions.length)
                        ];

                    String traffic = chooseTraffic(hour, day);

                    int scheduledMinutes = route.baseMinutes;

                    int delayMinutes = generateDelay(
                        hour, weather, traffic, day
                    );

                    int actualMinutes =
                        scheduledMinutes + delayMinutes;

                    String crowding = generateCrowding(
                        hour, traffic, day
                    );

                    writer.printf(
                        "%s,%s,%s,%s,%s,%d,%s,%s,%d,%d,%d,%s%n",
                        route.id,
                        route.busNumber,
                        route.source,
                        route.destination,
                        day,
                        hour,
                        weather,
                        traffic,
                        scheduledMinutes,
                        actualMinutes,
                        delayMinutes,
                        crowding
                    );
                }
            }
        }
    }

    private static String chooseTraffic(int hour, String day) {
        boolean weekend = day.equals("Saturday")
                       || day.equals("Sunday");

        int rushHourChance = weekend ? 35 : 65;

        if ((hour >= 7 && hour <= 10)
                || (hour >= 16 && hour <= 19)) {
            if (random.nextInt(100) < rushHourChance) {
                return "High";
            }
        }

        int choice = random.nextInt(100);

        if (choice < 30) {
            return "Low";
        } else if (choice < 75) {
            return "Medium";
        } else {
            return "High";
        }
    }

    private static int generateDelay(
            int hour, String weather, String traffic, String day) {

        int delay = random.nextInt(5); // Base delay: 0–4 minutes

        if (traffic.equals("Medium")) {
            delay += 2 + random.nextInt(4);
        } else if (traffic.equals("High")) {
            delay += 5 + random.nextInt(9);
        }

        if (weather.equals("Rain")) {
            delay += 3 + random.nextInt(6);
        } else if (weather.equals("Cloudy")) {
            delay += random.nextInt(3);
        }

        if ((hour >= 7 && hour <= 10)
                || (hour >= 16 && hour <= 19)) {
            delay += random.nextInt(5);
        }

        if (day.equals("Saturday") || day.equals("Sunday")) {
            delay = Math.max(0, delay - random.nextInt(3));
        }

        return delay;
    }

    private static String generateCrowding(
            int hour, String traffic, String day) {

        int score = 0;

        // Simulated passenger-demand patterns
        if ((hour >= 7 && hour <= 10)
                || (hour >= 16 && hour <= 19)) {
            score += 2;
        }

        if (traffic.equals("High")) {
            score += 1;
        }

        if (traffic.equals("Low")) {
            score -= 1;
        }

        if (day.equals("Saturday") || day.equals("Sunday")) {
            score -= 1;
        }

        score += random.nextInt(3) - 1;

        if (score <= 0) {
            return "Low";
        } else if (score <= 2) {
            return "Medium";
        } else {
            return "High";
        }
    }
}
