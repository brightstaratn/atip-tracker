from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import ATIPRequest, Document, ATIPRequestStatus
from .forms import ATIPRequestForm, DocumentUploadForm, StatusUpdateForm
from .models import ATIPRequest, Document, StatusTransition, ATIPRequestStatus


@login_required
def create_request(request):
    if request.method == 'POST':
        form = ATIPRequestForm(request.POST)
        if form.is_valid():
            try:
                atip_request = form.save(commit=False)
                atip_request.user = request.user
                atip_request.save()
                messages.success(request, 'ATIP Request created successfully!')
                return redirect('request_detail', request_id=atip_request.id)
            except Exception as e:
                messages.error(request, f'Error creating request: {str(e)}')
    else:
        form = ATIPRequestForm()
    
    return render(request, 'requests/create_request.html', {'form': form})


@login_required
def request_detail(request, request_id):
    try:
        # Fetch the specific request
        atip_request = get_object_or_404(ATIPRequest, id=request_id)

        # Document upload handling
        if request.method == 'POST':
            doc_form = DocumentUploadForm(request.POST, request.FILES)
            if doc_form.is_valid():
                try:
                    document = doc_form.save(commit=False)
                    document.request = atip_request
                    document.save()
                    messages.success(request, 'Document uploaded successfully!')
                    return redirect('request_detail', request_id=request_id)
                except Exception as e:
                    messages.error(request, f'Error uploading document: {str(e)}')
            else:
                messages.error(request, 'Invalid document upload form')
        else:
            doc_form = DocumentUploadForm()

        # Status update form
        status_form = StatusUpdateForm(instance=atip_request)

        return render(request, 'requests/request_detail.html', {
            'request': atip_request,
            'documents': atip_request.documents.all(),
            'doc_form': doc_form,
            'form': status_form
        })

    except Exception as e:
        messages.error(request, f"Error accessing request: {e}")
        return redirect('home')


@login_required
def update_request_status(request, request_id):
    atip_request = get_object_or_404(ATIPRequest, id=request_id)
    
    if request.method == 'POST':
        form = StatusUpdateForm(request.POST, instance=atip_request)
        if form.is_valid():
            form.save()
            messages.success(request, 'Request status updated successfully!')
            return redirect('request_detail', request_id=request_id)
    else:
        form = StatusUpdateForm(instance=atip_request)
    
    return render(request, 'requests/update_status.html', {'form': form})

@login_required
def request_list(request):
    # Fetch all requests for the current user
    requests = ATIPRequest.objects.filter(user=request.user).order_by('-created_at')
    
    # Optional: Add filtering and search functionality
    status = request.GET.get('status')
    if status:
        requests = requests.filter(status=status)
    
    context = {
        'requests': requests,
        'statuses': ATIPRequestStatus.choices # If you want to show status filter options
    }
    
    return render(request, 'requests/request_list.html', context)


@login_required
def edit_request(request, request_id):
    # Fetch the specific request, ensuring it belongs to the current user
    atip_request = get_object_or_404(ATIPRequest, id=request_id, user=request.user)
    
    if request.method == 'POST':
        form = ATIPRequestForm(request.POST, instance=atip_request)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Request updated successfully!')
                return redirect('request_detail', request_id=atip_request.id)
            except Exception as e:
                messages.error(request, f'Error updating request: {str(e)}')
    else:
        form = ATIPRequestForm(instance=atip_request)
    
    return render(request, 'requests/edit_request.html', {
        'form': form,
        'request': atip_request
    })


@login_required
def update_request_status(request, request_id):
    atip_request = get_object_or_404(ATIPRequest, id=request_id)
    
    if request.method == 'POST':
        form = StatusUpdateForm(request.POST, instance=atip_request)
        if form.is_valid():
            # Track status transition
            old_status = atip_request.status
            atip_request = form.save()
            
            # Create status transition record
            StatusTransition.objects.create(
                request=atip_request,
                from_status=old_status,
                to_status=atip_request.status,
                notes=form.cleaned_data.get('notes', '')
            )
            
            messages.success(request, 'Request status updated successfully!')
            return redirect('request_detail', request_id=atip_request.id)
    else:
        form = StatusUpdateForm(instance=atip_request)
    
    return render(request, 'requests/update_status.html', {'form': form})
