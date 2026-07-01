import type { NotificationProvider } from "@refinedev/core";
import { toast } from "sonner";

export const notificationProvider: NotificationProvider = {
	open: ({ key, message, description, type }) => {
		if (type === "error") {
			toast.error(message, { id: key, description });
		} else if (type === "success") {
			toast.success(message, { id: key, description });
		} else {
			toast(message, { id: key, description });
		}
	},
	close: (key) => {
		toast.dismiss(key);
	},
};
