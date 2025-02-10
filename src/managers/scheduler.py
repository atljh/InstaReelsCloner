from datetime import datetime, timedelta
from console import console


class Scheduler:
    def __init__(self, config):
        self.folder_1 = config["folder_1"]["folder_name"]
        self.folder_2 = config["folder_2"]["folder_name"]
        self.folder_1_times = config["folder_1"]["times"]
        self.folder_2_times = config["folder_2"]["times"]
        self.folder_1_descriptions = config["folder_1"]["descriptions"]
        self.folder_2_descriptions = config["folder_2"]["descriptions"]

    def get_scheduled_folder(self):
        current_time = datetime.now().strftime("%H:%M")

        if current_time in self.folder_1_times:
            return self.folder_1, self.folder_1_descriptions
        if current_time in self.folder_2_times:
            return self.folder_2, self.folder_2_descriptions

        self.print_next_schedule(current_time)
        return None, None

    def print_next_schedule(self, current_time):
        nearest_1 = self._get_nearest_time(self.folder_1_times, current_time)
        nearest_2 = self._get_nearest_time(self.folder_2_times, current_time)

        console.print(f"\n[cyan]🕒 Текущее время: {current_time}[/cyan]")
        console.print(f"[yellow]⏳ Следующее видео из {self.folder_1}: {nearest_1} ({self._get_time_difference(current_time, nearest_1)})[/yellow]")
        console.print(f"[yellow]⏳ Следующее видео из {self.folder_2}: {nearest_2} ({self._get_time_difference(current_time, nearest_2)})[/yellow]")

    def _get_nearest_time(self, times, current_time):
        current = datetime.strptime(current_time, "%H:%M")
        nearest_time = None
        min_difference = timedelta.max

        for time in times:
            target = datetime.strptime(time, "%H:%M")
            if target < current:
                target += timedelta(days=1)

            difference = target - current
            if difference < min_difference:
                min_difference = difference
                nearest_time = time
        return nearest_time

    def _get_time_difference(self, current_time, target_time):
        current = datetime.strptime(current_time, "%H:%M")
        target = datetime.strptime(target_time, "%H:%M")

        if target < current:
            target += timedelta(days=1)

        difference = target - current
        hours, remainder = divmod(difference.seconds, 3600)
        minutes = remainder // 60

        return f"{hours} ч {minutes} мин" if hours > 0 else f"{minutes} мин"
