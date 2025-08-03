# 🏥 Hospital Management System API

A comprehensive REST API for managing hospitals, patients, staff, beds, and medical inventory with MongoDB backend.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install required packages
pip install -r requirements.txt
```

### 2. Setup MongoDB
Make sure MongoDB is running on `localhost:27017`. 

**Windows Installation:**
```bash
# Download MongoDB Community Server from https://www.mongodb.com/try/download/community
# Install and start the MongoDB service
```

### 3. Start the API Server
```bash
python start_api.py
```

The API will be available at: `http://localhost:5000`

### 4. Test the API
Open `frontend_demo.html` in your web browser to interact with the API through a user-friendly interface.

## 📋 API Documentation

### Base URL
```
http://localhost:5000/api
```

### Available Endpoints

#### 🏥 Hospital Management
- `GET /api/hospitals` - Get all hospitals
- `POST /api/hospitals` - Create a new hospital
- `GET /api/hospitals/{id}` - Get hospital by ID
- `PUT /api/hospitals/{id}` - Update hospital
- `GET /api/hospitals/{id}/dashboard` - Get hospital dashboard
- `PUT /api/hospitals/{id}/deactivate` - Deactivate hospital
- `GET /api/hospitals/search?q={term}` - Search hospitals

#### 🛏️ Bed Management
- `GET /api/hospitals/{id}/beds` - Get hospital beds
- `POST /api/hospitals/{id}/beds` - Create bed
- `PUT /api/beds/{id}/status` - Update bed status

#### 👥 Patient Management
- `GET /api/hospitals/{id}/patients` - Get hospital patients
- `POST /api/hospitals/{id}/patients` - Admit patient
- `GET /api/patients/{id}` - Get patient by ID
- `PUT /api/patients/{id}/discharge` - Discharge patient

#### 👨‍⚕️ Staff Management
- `GET /api/hospitals/{id}/staff` - Get hospital staff
- `POST /api/hospitals/{id}/staff` - Add staff member
- `PUT /api/staff/{id}/status` - Update staff status
- `POST /api/staff/login` - Staff login

#### 💊 Inventory Management
- `GET /api/hospitals/{id}/inventory` - Get hospital inventory
- `POST /api/hospitals/{id}/inventory` - Add inventory item
- `PUT /api/inventory/{id}/stock` - Update inventory stock
- `GET /api/hospitals/{id}/inventory/low-stock` - Get low stock items

#### 🔧 System Management
- `GET /api/system/overview` - Get system overview
- `POST /api/initialize-sample-data` - Initialize sample data
- `GET /api/health` - Health check
- `GET /api/docs` - API documentation

## 🌐 Frontend Integration

### Example: Creating a Hospital
```javascript
async function createHospital() {
    const hospitalData = {
        hospital_id: 'HOSP003',
        name: 'City General Hospital',
        address: '123 Main Street',
        city: 'New York',
        state: 'NY',
        zip_code: '10001',
        phone: '555-0123',
        total_beds: 100,
        icu_beds: 10,
        emergency_beds: 5,
        departments: ['Emergency', 'ICU', 'General', 'Surgery']
    };

    const response = await fetch('http://localhost:5000/api/hospitals', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(hospitalData)
    });

    const result = await response.json();
    console.log(result);
}
```

### Example: Getting Hospital Dashboard
```javascript
async function getHospitalDashboard(hospitalId) {
    const response = await fetch(`http://localhost:5000/api/hospitals/${hospitalId}/dashboard`);
    const result = await response.json();
    
    if (result.success) {
        console.log('Hospital Info:', result.data.hospital_info);
        console.log('Summary:', result.data.summary);
        console.log('Alerts:', result.data.alerts);
    }
}
```

### Example: Admitting a Patient
```javascript
async function admitPatient() {
    const patientData = {
        patient_id: 'PAT001',
        first_name: 'John',
        last_name: 'Doe',
        age: 35,
        gender: 'male',
        phone: '555-0123',
        emergency_contact: 'Jane Doe - 555-0124',
        admission_reason: 'Routine checkup'
    };

    const response = await fetch('http://localhost:5000/api/hospitals/HOSP001/patients', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(patientData)
    });

    const result = await response.json();
    console.log(result);
}
```

## 📊 API Response Format

All API responses follow this format:

### Success Response
```json
{
    "success": true,
    "data": {
        // Response data here
    }
}
```

### Error Response
```json
{
    "success": false,
    "error": "Error message here"
}
```

## 🔗 Cross-Origin Requests (CORS)

The API is configured to accept requests from any origin, making it suitable for web frontend development. CORS is enabled for all routes.

## 🗄️ Database Structure

### Collections:
- `hospitals` - Hospital information
- `beds` - Hospital beds with room assignments
- `patients` - Patient records and admission history
- `staff` - Staff members and authentication
- `medical_inventory` - Medical supplies and medications
- `departments` - Hospital departments

### Hospital-Specific Data:
All collections use `hospital_id` field to segregate data by hospital, ensuring proper data isolation.

## 🛠️ Development

### Project Structure
```
Hospital_website_Terrahacks/
├── backend/
│   ├── api.py              # REST API server
│   ├── hospital.py         # Hospital management system
│   ├── hospital_beds.py    # Bed management
│   ├── patient_data.py     # Patient management
│   ├── med_inv.py         # Medical inventory
│   └── staff_inv.py       # Staff management
├── frontend_demo.html      # Frontend demo
├── start_api.py           # API server launcher
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

### Adding New Endpoints
1. Add the endpoint function to `backend/api.py`
2. Follow the existing pattern for error handling and JSON responses
3. Test with the frontend demo or API testing tools

### Environment Variables
Create a `.env` file in the root directory:
```
MONGO_URI=mongodb://localhost:27017/
```

## 🚨 Production Deployment

For production deployment:

1. **Use a production WSGI server** (like Gunicorn):
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 backend.api:app
   ```

2. **Set environment variables**:
   ```bash
   export MONGO_URI=mongodb://your-mongo-host:27017/
   export FLASK_ENV=production
   ```

3. **Configure reverse proxy** (nginx/Apache)
4. **Enable HTTPS**
5. **Set up proper authentication and authorization**

## 🧪 Testing

### Test the API Health
```bash
curl http://localhost:5000/api/health
```

### Initialize Sample Data
```bash
curl -X POST http://localhost:5000/api/initialize-sample-data
```

### Get All Hospitals
```bash
curl http://localhost:5000/api/hospitals
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the API documentation at `/api/docs`
- Use the frontend demo for interactive testing
- Ensure MongoDB is running and accessible

---

**🎉 Congratulations!** You now have a fully functional Hospital Management System API that your frontend can communicate with over the internet!
