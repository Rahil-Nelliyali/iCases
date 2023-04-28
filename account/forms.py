from django import forms
from .models import Account
from orders.models import Address



class RegistrationForm(forms.ModelForm):
  
  password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter Password', 'style':'background: #171717; border:0;color:white;'}))
  confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'style':'background: #171717; border:0;color:white;'}))
                                                                
    
  class Meta:
    model = Account
    fields = ['first_name', 'last_name', 'email', 'phone_number',]
    
  def __init__(self, *args, **kwargs):
    super(RegistrationForm,self).__init__(*args, **kwargs)
    self.fields['first_name'].widget.attrs['placeholder'] = ' First Name'
    self.fields['first_name'].widget.attrs['style'] = 'background: #171717;color:white; border:0;box-shadow: none;text-align:left;:focus:border:'
    self.fields['last_name'].widget.attrs['placeholder'] = ' Last Name'
    self.fields['last_name'].widget.attrs['style'] = 'background: #171717; border:0;color:white;'
    self.fields['email'].widget.attrs['placeholder'] = ' Email Address'
    self.fields['email'].widget.attrs['style'] = 'background: #171717; border:0;color:white;'
    self.fields['phone_number'].widget.attrs['placeholder'] = ' Mobile Number'
    self.fields['phone_number'].widget.attrs['style'] = 'background: #171717; border:0;color:white;'
    self.fields['phone_number'].widget.attrs['maxlength'] = 10

    for field  in self.fields:
      self.fields[field].widget.attrs['class'] = 'form-control'
  
  def clean(self):
    cleaned_data = super(RegistrationForm, self).clean()
    password = cleaned_data.get('password')
    confirm_password = cleaned_data.get('confirm_password')
    
    if password != confirm_password:
      raise forms.ValidationError("Password does not match!!")
    
class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields  = ['first_name','last_name', 'email', 'phone_number',]

    def __init__(self, *args, **kwargs):
        super(UserForm,self).__init__(*args, **kwargs)  
        for field  in self.fields:
             self.fields[field].widget.attrs['class'] = 'form-control'
             
class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields=['first_name','last_name','phone','email','address_line1','address_line2','district','state','city', 'pincode']
    
    def __init__(self, *args, **kwargs):
      super(AddressForm,self).__init__(*args, **kwargs)  
      for field  in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
             