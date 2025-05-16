import tkinter as tk #Xây dựng giao diện
from tkinter import filedialog, messagebox, ttk
import pandas as pd #Xử lý dữ liệu
from scipy.stats import pearsonr #Tính toán tương quan Pearson
import numpy as np #Tính toán số học
import matplotlib.pyplot as plt #Vẽ biểu đồ
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class PearsonCorrelationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ứng dụng Tương quan Pearson")
        self.state('zoomed')  # Chạy full màn hình
        self.configure(bg="#f4f4f4")

        self.df = None
        self.file_path = None

        # Frame chọn file
        self.file_frame = ttk.LabelFrame(self, text="Chọn dữ liệu")
        self.file_frame.pack(padx=10, pady=10, fill="x")

        self.browse_button = ttk.Button(self.file_frame, text="Chọn file CSV", command=self.browse_file)
        self.browse_button.pack(padx=5, pady=5)

        self.file_label = ttk.Label(self.file_frame, text="Chưa có file nào được chọn", foreground="red")
        self.file_label.pack()

        # Frame chọn cột
        self.column_frame = ttk.LabelFrame(self, text="Chọn biến để phân tích")
        self.column_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(self.column_frame, text="Chọn cột X:").pack()
        self.x_combobox = ttk.Combobox(self.column_frame, state="disabled")
        self.x_combobox.pack()
        
        ttk.Label(self.column_frame, text="Chọn cột Y:").pack()
        self.y_combobox = ttk.Combobox(self.column_frame, state="disabled")
        self.y_combobox.pack()

        self.analyze_button = ttk.Button(self.column_frame, text="Phân tích", state="disabled", command=self.analyze)
        self.analyze_button.pack(pady=10)

        # Frame chính chứa kết quả và biểu đồ
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Frame kết quả (bên trái)
        self.result_frame = ttk.LabelFrame(self.main_frame, text="Kết quả")
        self.result_frame.pack(side="left", padx=10, pady=10, fill="both", expand=True)

        self.result_text = tk.Text(self.result_frame, height=20, wrap="word")
        self.result_text.pack(fill="both", expand=True, padx=5, pady=5)

        # Frame biểu đồ (bên phải)
        self.plot_frame = ttk.LabelFrame(self.main_frame, text="Biểu đồ")
        self.plot_frame.pack(side="right", padx=10, pady=10, fill="both", expand=True)

    def browse_file(self):
        file_path = filedialog.askopenfilename(title="Chọn file CSV", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if file_path:
            try:
                self.df = pd.read_csv(file_path)
                self.file_path = file_path
                self.file_label.config(text=f"File đã chọn: {file_path.split('/')[-1]}", foreground="green")
                
                columns = list(self.df.columns)
                self.x_combobox["values"] = columns
                self.y_combobox["values"] = columns
                self.x_combobox.config(state="readonly")
                self.y_combobox.config(state="readonly")
                self.analyze_button.config(state="normal")

            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể đọc file CSV:\n{e}")

    def analyze(self):
        x_col = self.x_combobox.get()
        y_col = self.y_combobox.get()

        if not x_col or not y_col:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn cả cột X và cột Y.")
            return
        if x_col == y_col:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn hai cột khác nhau.")
            return

        try:
            data = self.df[[x_col, y_col]].dropna()
            x_data, y_data = data[x_col], data[y_col]
            n = len(x_data)
            
            result_message = "**Bước 1: Loại bỏ giá trị NaN**\n"
            result_message += f"Dữ liệu còn lại: {n} dòng\n\n"
            
            # Bước 2: Tính tổng và trung bình
            result_message += "**Bước 2: Tính tổng và trung bình**\n"
            sum_x = np.sum(x_data)
            sum_y = np.sum(y_data)
            mean_x = np.mean(x_data)
            mean_y = np.mean(y_data)
            result_message += f"Tổng X: {sum_x:.3f}\n"
            result_message += f"Tổng Y: {sum_y:.3f}\n"
            result_message += f"Trung bình X: {mean_x:.3f}\n"
            result_message += f"Trung bình Y: {mean_y:.3f}\n\n"
            
            # Bước 3: Tính độ lệch so với trung bình
            result_message += "**Bước 3: Tính độ lệch so với trung bình**\n"
            x_dev = x_data - mean_x
            y_dev = y_data - mean_y
            result_message += "Độ lệch X: " + ", ".join([f"{val:.3f}" for val in x_dev]) + "\n"
            result_message += "Độ lệch Y: " + ", ".join([f"{val:.3f}" for val in y_dev]) + "\n\n"
            
            # Bước 4: Tính bình phương độ lệch
            result_message += "**Bước 4: Tính bình phương độ lệch**\n"
            x_dev_sq = x_dev ** 2
            y_dev_sq = y_dev ** 2
            sum_x_dev_sq = np.sum(x_dev_sq)
            sum_y_dev_sq = np.sum(y_dev_sq)
            result_message += f"Tổng (X - mean_X)^2: {sum_x_dev_sq:.3f}\n"
            result_message += f"Tổng (Y - mean_Y)^2: {sum_y_dev_sq:.3f}\n\n"
            
            # Bước 5: Tính tích độ lệch
            result_message += "**Bước 5: Tính tích độ lệch**\n"
            xy_dev_prod = x_dev * y_dev
            sum_xy_dev_prod = np.sum(xy_dev_prod)
            result_message += f"Tổng (X - mean_X)*(Y - mean_Y): {sum_xy_dev_prod:.3f}\n\n"
            
            # Bước 6: Tính hệ số tương quan Pearson
            result_message += "**Bước 6: Tính hệ số tương quan Pearson**\n"
            r = sum_xy_dev_prod / (np.sqrt(sum_x_dev_sq) * np.sqrt(sum_y_dev_sq))
            result_message += f"r = {sum_xy_dev_prod:.3f} / (sqrt({sum_x_dev_sq:.3f}) * sqrt({sum_y_dev_sq:.3f})) = {r:.3f}\n\n"
            
            # Đánh giá mức độ tương quan
            result_message += "**Đánh giá mức độ tương quan:**\n"
            abs_r = abs(r)
            if abs_r >= 0.80:
                correlation_strength = "Rất mạnh"
            elif abs_r >= 0.60:
                correlation_strength = "Mạnh"
            elif abs_r >= 0.40:
                correlation_strength = "Trung bình"
            elif abs_r >= 0.20:
                correlation_strength = "Yếu"
            else:
                correlation_strength = "Rất yếu"
                
            correlation_direction = "Dương (Thuận)" if r > 0 else "Âm (Nghịch)" if r < 0 else "Không có tương quan"
            result_message += f"Mức độ tương quan: {correlation_strength}\n"
            result_message += f"Chiều tương quan: {correlation_direction}\n"
            result_message += f"Kết luận: Hai biến có mối tương quan {correlation_direction.lower()} với cường độ {correlation_strength.lower()}.\n\n"
            
            # Bước 7: Tính p-value
            result_message += "**Bước 7: Tính p-value(Đánh giá ý nghĩa của thống kê)**\n"
            _, p_value = pearsonr(x_data, y_data)
            result_message += f"p-value = {p_value:.4f}\n\n"
            
            # Bước 8: Tính khoảng tin cậy 95%
            result_message += "**Bước 8: Tính khoảng tin cậy 95%(Mức độ đáng tin)**\n"
            if n > 3 and abs(r) < 1:
                z = np.arctanh(r)
                se = 1 / np.sqrt(n - 3)
                z_crit = 1.96
                r_low, r_high = np.tanh([z - z_crit * se, z + z_crit * se])
                result_message += f"Khoảng tin cậy 95%: [{r_low:.3f}, {r_high:.3f}]\n\n"
            else:
                result_message += "Không thể tính khoảng tin cậy (n quá nhỏ hoặc r=±1).\n\n"

            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, result_message)

            # Vẽ biểu đồ scatter plot
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.scatter(x_data, y_data, color='blue', label='Dữ liệu')
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            ax.set_title(f"Scatter Plot: {x_col} vs {y_col}")
            ax.legend()
            ax.grid(True)

            for widget in self.plot_frame.winfo_children():
                widget.destroy()
            canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tính toán: {e}")

if __name__ == "__main__":
    app = PearsonCorrelationApp()
    app.mainloop()