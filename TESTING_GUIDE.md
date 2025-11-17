# Testing Guide: Applicant Location Map Feature

## Prerequisites
- Django development server running
- At least one recruiter account
- At least one job seeker account with location data
- A job posting created by the recruiter

## Test Scenarios

### Scenario 1: Basic Map Functionality

**Setup:**
1. Create a job seeker profile with location enabled
2. Set latitude/longitude on the profile (e.g., 33.7756, -84.3963 for Atlanta)
3. Apply to a job
4. Login as the recruiter who posted the job

**Steps:**
1. Navigate to "My Jobs"
2. Click on a job with applications
3. Click "Application Pipeline"
4. Click "View Applicant Map" button
5. Verify map loads with applicant markers
6. Click on a marker to see applicant details
7. Verify popup shows correct information

**Expected Results:**
- Map displays centered on applicants
- Markers are color-coded by status
- Popup shows applicant name, location, status, and date
- "View in Pipeline" link works

### Scenario 2: Privacy Settings

**Setup:**
1. Create multiple job seeker profiles
2. Some with `show_location = True`, some with `False`
3. All apply to the same job

**Steps:**
1. Login as recruiter
2. Navigate to applicant map
3. Verify only applicants with location sharing enabled appear

**Expected Results:**
- Only applicants with `show_location = True` are shown
- Count badge shows correct number
- Privacy message displayed if no locations shared

### Scenario 3: Clustering Behavior

**Setup:**
1. Create 5+ job seekers in close proximity (same city)
2. All apply to the same job

**Steps:**
1. Login as recruiter
2. View applicant map
3. Observe cluster icon
4. Click cluster to zoom in
5. Verify individual markers appear

**Expected Results:**
- Nearby applicants cluster together
- Cluster shows number of applicants
- Clicking cluster zooms to show individuals
- Markers separate as you zoom in

### Scenario 4: Multiple Status Colors

**Setup:**
1. Create applicants in different statuses:
   - Applied
   - Review
   - Interview
   - Offer
   - Closed

**Steps:**
1. View applicant map
2. Observe marker colors

**Expected Results:**
- Different colors for each status:
  - Cyan/Light Blue: Applied
  - Blue: Review
  - Yellow: Interview
  - Green: Offer
  - Gray: Closed

### Scenario 5: Empty States

**Test 5a: No Applicants**
1. Create a job with no applications
2. Try to access applicant map
3. Verify appropriate message

**Test 5b: No Location Data**
1. Create applicants without location data
2. View map
3. Verify "no location sharing" message

### Scenario 6: Existing Job Location Map

**Setup:**
1. Create/edit a job
2. Add latitude/longitude coordinates
3. Save the job

**Steps:**
1. View job detail page (as any user)
2. Scroll to "Office Location" section
3. Verify map displays correctly

**Expected Results:**
- Map shows office location
- Marker has company name popup
- Map is responsive

### Scenario 7: Security Testing

**Test 7a: Non-Recruiter Access**
1. Login as job seeker
2. Try to access `/jobs/<job_id>/applicants-map/`
3. Should be denied

**Test 7b: Wrong Recruiter**
1. Login as Recruiter A
2. Try to access Recruiter B's job map
3. Should be denied

**Test 7c: AJAX Endpoint Security**
1. Test AJAX endpoint without authentication
2. Test with wrong user type
3. Test with different recruiter's job

**Expected Results:**
- All unauthorized access attempts return 403 or redirect
- Error messages displayed appropriately

## Performance Testing

### Test 8: Large Number of Applicants

**Setup:**
1. Create 50+ applicants for a single job
2. Distribute across different locations

**Steps:**
1. Load applicant map
2. Observe clustering performance
3. Test zoom interactions
4. Check browser console for errors

**Expected Results:**
- Map loads within 2-3 seconds
- Smooth clustering animations
- No console errors
- Responsive zoom behavior

## Browser Testing

Test the feature in:
- Google Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Microsoft Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Common Issues & Solutions

### Issue 1: Map Not Loading
**Symptoms:** Blank space where map should be
**Check:**
- Browser console for JavaScript errors
- Leaflet CSS/JS files loading correctly
- Network tab for failed requests

### Issue 2: Markers Not Showing
**Symptoms:** Map loads but no markers
**Check:**
- Applicants have valid latitude/longitude
- `show_location = True` for profiles
- AJAX endpoint returning data (check Network tab)
- Browser console for errors

### Issue 3: Clustering Not Working
**Symptoms:** Individual markers instead of clusters
**Check:**
- Leaflet.markercluster plugin loading
- Markers are close enough to cluster
- Check browser console for plugin errors

### Issue 4: Permission Denied
**Symptoms:** 403 error or redirect
**Check:**
- User is logged in
- User is a recruiter
- Recruiter owns the job
- Check server logs for details

## Test Data Examples

### Sample Job Seeker Locations (US Cities)
```python
# Atlanta, GA
latitude = 33.7756
longitude = -84.3963

# New York, NY
latitude = 40.7128
longitude = -74.0060

# San Francisco, CA
latitude = 37.7749
longitude = -122.4194

# Chicago, IL
latitude = 41.8781
longitude = -87.6298

# Austin, TX
latitude = 30.2672
longitude = -97.7431
```

## Reporting Bugs

When reporting issues, include:
1. Browser and version
2. Steps to reproduce
3. Expected vs actual behavior
4. Screenshots/screen recording
5. Browser console errors
6. Django server logs (if applicable)

## Success Criteria

✅ All test scenarios pass
✅ No console errors
✅ Privacy settings respected
✅ Security checks pass
✅ Responsive on mobile
✅ Clustering works smoothly
✅ Existing job map still works
