# Applicant Location Map Feature

## Overview
This document describes the implementation of the **Applicant Location Clustering Map** feature for recruiters in the Job Finder application.

## Feature Description
As a Recruiter, you can now see clusters of applicants by location on an interactive map to understand where most candidates are coming from. This helps recruiters make informed decisions about hiring locations, relocation assistance, and geographic distribution of talent.

## Implementation Details

### 1. Backend Changes

#### Models (`jobs/models.py`)
- **Added fields to Job model:**
  - `latitude` (FloatField, blank=True, null=True)
  - `longitude` (FloatField, blank=True, null=True)
- These fields store the job's office location coordinates for display on the job detail page

#### Views (`jobs/views.py`)
- **New view: `applicants_map(request, job_id)`**
  - Restricted to recruiters only
  - Verifies the recruiter owns the job
  - Renders the applicant map page

#### AJAX Views (`jobs/ajax_views.py`)
- **New endpoint: `get_applicant_locations(request, job_id)`**
  - Returns JSON data of applicant locations
  - Respects privacy settings (`Profile.show_location`)
  - Returns applicant details including:
    - Name
    - Location coordinates (latitude/longitude)
    - Location text
    - Application status
    - Applied date
    - Application ID

#### URL Routes (`jobs/urls.py`)
- **New routes:**
  - `/jobs/<job_id>/applicants-map/` - Main applicant map page
  - `/jobs/ajax/<job_id>/applicant-locations/` - AJAX endpoint for location data

### 2. Frontend Changes

#### New Template (`templates/jobs/applicants_map.html`)
- **Features:**
  - Interactive Leaflet.js map with OpenStreetMap tiles
  - Leaflet.markercluster plugin for clustering nearby applicants
  - Color-coded markers by application status:
    - 🔵 Blue (Applied) - Recently Applied
    - 🔷 Light Blue (Review) - Under Review
    - 🟡 Yellow (Interview) - Interview Stage
    - 🟢 Green (Offer) - Offer Extended
    - ⚪ Gray (Closed) - Application Closed
  - Popup information on each marker showing:
    - Applicant name
    - Location
    - Application status
    - Applied date
    - Link to view in pipeline
  - Automatic map bounds adjustment to show all applicants
  - Privacy-aware: Only shows applicants who enabled location sharing
  - Breadcrumb navigation
  - Legend explaining status badges
  - Link to view application pipeline

#### Updated Template (`templates/jobs/application_pipeline.html`)
- Added "View Applicant Map" button in the header
- Provides easy navigation between pipeline and map views

### 3. Privacy & Security

#### Privacy Considerations
- **Respects user privacy settings:**
  - Only displays applicants who have `Profile.show_location = True`
  - Shows notification when no applicants have location sharing enabled
  - Applicants control their location visibility in profile settings

#### Security Measures
- Login required for all map endpoints
- Recruiter-only access (verified by user type)
- Job ownership verification (recruiter can only see their own job's applicants)
- Proper error handling and user feedback

### 4. User Experience

#### For Recruiters
1. Navigate to a job's application pipeline
2. Click "View Applicant Map" button
3. See an interactive map with clustered applicant locations
4. Click clusters to zoom in and see individual applicants
5. Click markers to see applicant details and navigate to pipeline

#### Visual Features
- Responsive design works on all screen sizes
- Cluster icons change size/color based on number of applicants
- Smooth zoom transitions
- Clear legend and help text
- Loading states and error messages

### 5. Technical Stack

#### Libraries Used
- **Leaflet.js v1.9.4** - Open-source interactive map library
- **Leaflet.markercluster v1.5.3** - Marker clustering plugin
- **OpenStreetMap** - Free map tile provider
- **Bootstrap 5** - UI components and styling

#### Browser Compatibility
- Modern browsers (Chrome, Firefox, Safari, Edge)
- Requires JavaScript enabled
- Mobile-responsive

### 6. Testing Recommendations

#### Manual Testing
1. **Test as recruiter with applicants:**
   - Verify map loads correctly
   - Check clustering works properly
   - Confirm privacy settings are respected
   - Test marker popups and navigation

2. **Test edge cases:**
   - Job with no applicants
   - Job with applicants but no location sharing
   - Multiple applicants in same location
   - Single applicant

3. **Test existing map functionality:**
   - Job detail page office location map
   - Verify latitude/longitude fields save correctly in job form
   - Test map display for jobs with and without coordinates

#### Security Testing
- Attempt to access map as non-recruiter
- Attempt to access another recruiter's job map
- Verify AJAX endpoint authorization

### 7. Future Enhancements

Potential improvements for future iterations:
- Filter applicants by status on the map
- Heat map visualization option
- Export applicant location data
- Integration with geocoding API for automatic coordinate lookup
- Distance calculations from office location
- Search/filter functionality on map
- Custom map styles/themes

## Files Modified

### New Files
- `templates/jobs/applicants_map.html` - Main map template

### Modified Files
- `jobs/models.py` - Added latitude/longitude to Job model
- `jobs/views.py` - Added applicants_map view
- `jobs/ajax_views.py` - Added get_applicant_locations endpoint
- `jobs/urls.py` - Added new routes
- `templates/jobs/application_pipeline.html` - Added map button

## Database Schema

### Job Model
```python
latitude = models.FloatField(blank=True, null=True)
longitude = models.FloatField(blank=True, null=True)
```

### Profile Model (already existed)
```python
latitude = models.FloatField(blank=True, null=True)
longitude = models.FloatField(blank=True, null=True)
show_location = models.BooleanField(default=True)
```

## API Endpoints

### GET `/jobs/<job_id>/applicants-map/`
- Renders the applicant map page
- Requires: Authenticated recruiter who owns the job
- Returns: HTML page with map

### GET `/jobs/ajax/<job_id>/applicant-locations/`
- Returns applicant location data as JSON
- Requires: Authenticated recruiter who owns the job
- Response format:
```json
{
  "success": true,
  "locations": [
    {
      "lat": 33.7756,
      "lng": -84.3963,
      "name": "John Doe",
      "location": "Atlanta, GA",
      "status": "Under Review",
      "status_code": "review",
      "applied_at": "Nov 15, 2024",
      "application_id": 123
    }
  ],
  "count": 1
}
```

## Conclusion

The Applicant Location Map feature is now fully implemented and provides recruiters with valuable geographic insights about their applicant pool. The feature respects user privacy, maintains security, and integrates seamlessly with the existing application pipeline functionality.
