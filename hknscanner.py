from tkinter import *
import gspread
from oauth2client.service_account import ServiceAccountCredentials

#### Access data spreadsheet ####
scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name('HKN Barcode Scanner-068aaeb7d73b.json', scope)
gc = gspread.authorize(credentials)
sh = gc.open_by_key('1NZJc2oPN9o_qWQq6CV7yCYGrmGwujlqfhEnhTBHTNKo')
users = sh.get_worksheet(0)
food = sh.get_worksheet(1)

foodData = food.get_all_values()

#### Controller for the app ####
class App(Tk):

        def __init__(self):
                Tk.__init__(self)

                container = Frame(self)
                container.pack(side="top", fill="both", expand=True)
                container.grid_rowconfigure(0, weight=1)
                container.grid_columnconfigure(0, weight=1)

                self.frames = {}
                for f in (ScanID, Balance, Decline, ItemSelect,
                	VerifyItem, ThankYou, AddCredit, VerifyAmt):
                        page_name = f.__name__
                        frame = f(parent=container, controller=self)
                        self.frames[page_name] = frame

                        frame.grid(row=0,column=0)

                self.show_frame("ScanID")

        def show_frame(self, page_name):
                for frame in self.frames.values():
                        frame.grid_remove()
                frame = self.frames[page_name]
                frame.grid()

        def accessID(self, id):
        	self.user = users.find(id)
        	self.userData = users.row_values(self.user.row)[:3]
        	
        	b = self.frames["Balance"]
        	b.labelBalance.config(text=("$" + \
        		str.format('{0:.2f}', float(self.userData[2]))))

        	if (float(self.userData[2]) > 20.0):
        	    self.show_frame("Decline")
        	else:
        		self.show_frame("Balance")


        def accessFood(self, id):
        	
        	self.foodItem = foodData[id[0]]

        	i = self.frames["ItemSelect"]
        	v = self.frames["VerifyItem"]
        	v.labelItem.config(text=i.listbox.get(id))

        	self.show_frame("VerifyItem")

        def updateID(self, amt):
        	print (self.userData[2])
        	print (amt)
        	newAmt = str(float(self.userData[2]) + float(amt)) 
        	users.update_cell(self.user.row, self.user.col + 2, newAmt)

        	self.show_frame("ThankYou")


#### User ID scanning screen ####
class ScanID(Frame):

	def __init__(self, parent, controller):
		Frame.__init__(self, parent)
		self.controller = controller

		labelScan = Label(self, text="Please scan ID:")
		entryID = Entry(self, show="*")
		entryID.focus()
		buttonClear = Button(self, text="CLEAR", 
			command=lambda: entryID.delete(0, END))
		buttonOk1 = Button(self, text="OK", bg="green", fg="white",
			command=lambda: controller.accessID(entryID.get()))

		labelScan.grid(row=0, columnspan=2)
		entryID.grid(row=1, columnspan=2)
		buttonClear.grid(row=2,column=0)
		buttonOk1.grid(row=2,column=1)		

#### User money balance screen ####
class Balance(Frame):

	def __init__(self, parent, controller):
		Frame.__init__(self, parent)
		self.controller = controller

		labelText = Label(self, text="Your balance:")
		self.labelBalance = Label(self)
		buttonCredit1 = Button(self, text="Add Credit",
			command=lambda: controller.show_frame("AddCredit"))
		buttonFood = Button(self, text="Buy Food",
			command=lambda: controller.show_frame("ItemSelect"))
		buttonBack1 = Button(self, text="BACK", bg="red", fg="white",
			command=lambda: controller.show_frame("ScanID"))

		labelText.grid(row=0, columnspan=3)
		self.labelBalance.grid(row=1, columnspan=3)
		buttonCredit1.grid(row=2,column=0)
		buttonFood.grid(row=2,column=1)
		buttonBack1.grid(row=2,column=2)

#### Large debt error screen ####
class Decline(Frame):

	def __init__(self, parent, controller):
		Frame.__init__(self, parent)
		self.controller = controller

		labelDecline = Label(self, text=("You currently owe too much money." + \
			" Please add funds"))
		buttonCredit2 = Button(self, text="Add Credit",
			command=lambda: controller.show_frame("AddCredit"))
		buttonBack2 = Button(self, text="BACK", bg="red", fg="white",
			command=lambda: controller.show_frame("ScanID"))

		labelDecline.grid(columnspan=2)
		buttonCredit2.grid(row=1,column=0)
		buttonBack2.grid(row=1,column=1)

#### Quick item purchase screen ####
class ItemSelect(Frame):

	def __init__(self, parent, controller):
		Frame.__init__(self, parent)
		self.controller = controller

		labelItem = Label(self, text="Please select item:")
		self.listbox = Listbox(self, selectmode=EXTENDED)
		buttonOk2 = Button(self, text="OK", bg="green", fg="white",
			command=lambda: controller.accessFood(self.listbox.curselection()))
		buttonBack3 = Button(self, text="BACK", bg="red", fg="white",
			command=lambda: controller.show_frame("Balance"))

		for item in foodData:
			self.listbox.insert(END, item[0] + " - $" + \
				str.format('{0:.2f}',float(item[1])))

		labelItem.grid(columnspan=2)
		self.listbox.grid(row=1, columnspan=2)
		buttonOk2.grid(row=2,column=0)
		buttonBack3.grid(row=2,column=1)

#### Item selection verification screen ####
class VerifyItem(Frame):

	def __init__(self, parent, controller):
		Frame.__init__(self, parent)
		self.controller = controller

		labelCorrect = Label(self, text="Is this correct?")
		self.labelItem = Label(self)
		buttonOk3 = Button(self, text="OK", bg="green", fg="white",
			command=lambda: controller.updateID("-" + controller.foodItem[1]))
		buttonBack4 = Button(self, text="BACK", bg="red", fg="white",
			command=lambda: controller.show_frame("ItemSelect"))

		labelCorrect.grid(columnspan=2)
		self.labelItem.grid(row=1, columnspan=2)
		buttonOk3.grid(row=2,column=0)
		buttonBack4.grid(row=2,column=1)

#### Finishing "Thank you" screen ####
class ThankYou(Frame):

	def __init__(self, parent, controller):
		Frame.__init__(self, parent)
		self.controller = controller

		labelThankYou = Label(self, text="Thank you!")
		buttonOk4 = Button(self, text="OK", bg="green", fg="white",
			command=lambda: controller.show_frame("ScanID"))

		labelThankYou.grid()
		buttonOk4.grid(row=1,column=0)

#### Adding funds screen ####
class AddCredit(Frame):

	def __init__(self, parent, controller):
		Frame.__init__(self, parent)
		self.controller = controller

		labelAmount = Label(self, text="Please enter amount:")
		buttonOk5 = Button(self, text="OK", bg="green", fg="white",
			command=lambda: controller.show_frame("VerifyAmt"))
		buttonBack5 = Button(self, text="BACK", bg="red", fg="white",
			command=lambda: controller.show_frame("Balance"))

		labelAmount.grid(columnspan=2)
		buttonOk5.grid(row=1,column=0)
		buttonBack5.grid(row=1,column=1)

#### Additional funds verification screen ####
class VerifyAmt(Frame):

	def __init__(self, parent, controller):
		Frame.__init__(self, parent)
		self.controller = controller

		labelCorrect = Label(self, text="Is this correct?")
		buttonOk6 = Button(self, text="OK", bg="green", fg="white",
			command=lambda: controller.show_frame("ThankYou"))
		buttonBack6 = Button(self, text="BACK", bg="red", fg="white",
			command=lambda: controller.show_frame("AddCredit"))

		labelCorrect.grid(columnspan=2)
		buttonOk6.grid(row=1,column=0)
		buttonBack6.grid(row=1,column=1)


#### Running the application ####
app = App()
app.title("HKN Food Scanner")
app.minsize(width=300, height=300)
app.maxsize(width=300, height=300)
app.mainloop()
