//--------------------------------------------------------------------------------------------//
// APPLICATION -> TRAPPER
//--------------------------------------------------------------------------------------------//

var app = angular.module('trapper', ['ngRoute', 'ngGrid', 'ngSanitize', 'ngUpload']).config(function($httpProvider) {
    $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
});


app.directive('datetimepicker', function() {
    return {
      require: 'ngModel',
	link: function(scope, el, attr, ngModel) {
		$(el).datetimepicker({
		    format: 'yyyy-mm-dd hh:ii',
		}).on(
		    'changeDate', function(ev){
			scope.$apply(function() {
			    ngModel.$setViewValue(el.val());
			});
		    });	
	}
    }
});


//--------------------------------------------------------------------------------------------//
// FACTORY -> GET/POST AJAX FORM
//--------------------------------------------------------------------------------------------//

// http://stackoverflow.com/questions/17629126/how-to-upload-a-file-using-angularjs-like-the-traditional-way
app.factory('formDataObject', function() {
    return function(data) {
        var fd = new FormData();
        angular.forEach(data, function(value, key) {
            fd.append(key, value);
        });
        return fd;
    };
});

app.factory('ajaxForm', function($http, $compile, $location, formDataObject){
    scope = this;
    return {
	ERROR_403_TEMPLATE : '<h3>PERMISSION DENIED (403)</h3><span>We are sorry but apparently you do not have a required permission to do what you want</span>',
	postAjaxForm : function(form_post_url, form_data, form_div) {
	    scope['form_data'] = {};
	    var post_params = {
		method: 'POST',
		url: form_post_url,
		data: form_data,
	    };
	    $http(
		post_params
	    ).success(function(out_data, status) {
		delete scope['form_data']
		var compiled_form_html = $compile(out_data['form_html'])(scope);
		$(form_div).empty();
		$(form_div).append(compiled_form_html);
		// select2 multiple choices field workaround
		setTimeout(function(){
		    $(form_div + ' select.selectmultiple').select2()
		},10);
		scope.msg_alert = "success";
		scope.msg_txt = out_data['msg'];
		return status
	    }).error(function(out_data, status) {
		if (out_data['form_html']) {
		    delete scope['form_data']
		    var compiled_form_html = $compile(out_data['form_html'])(scope);
		    $(form_div).empty();
		    $(form_div).append(compiled_form_html);
		    // select2 multiple choices field workaround
		    setTimeout(function(){
			$(form_div + ' select.selectmultiple').select2()
		    },10);
		};
		scope.msg_alert = "danger";
		scope.msg_txt = out_data['msg'];
		return status
	    });
	},
	getAjaxForm : function(form_get_url, form_div, use_selections) {
	    use_selections = typeof use_selections !== 'undefined' ? use_selections : false;
	    if (use_selections) {
		scope.form_with_selections = true
	    } else {
		scope.form_with_selections = false
	    }
	    scope.msg_alert = '';
	    scope.msg_txt = '';
	    $http.get(form_get_url
		     ).success(function(out_data, status) {
			 if (out_data['initial']) {
			     scope[out_data['model']+'_data'] = JSON.parse(out_data['initial']);
			 } else {
			     scope[out_data['model']+'_data'] = {};
			 };
			 var compiled_form_html = $compile(out_data['form_html'])(scope);
			 $(form_div).empty();
			 $(form_div).append(compiled_form_html);
			 // select2 multiple choices field workaround
			 setTimeout(function(){
			     $(form_div + ' select.selectmultiple').select2()
			 },10);
			 return status
		     }).error(function(out_data, status) {
			 scope.modal_form_header = 'Error'
			 $(form_div).empty();
			 if (status == 403) {
			     $(form_div).append(scope.ERROR_403_TEMPLATE);
			 }
			 return status
		     });
	}, 
    }
});

// TODO: change all hard-coded urls below to sth more generic
// http://django-angular.readthedocs.org/en/latest/manage-urls.html

//--------------------------------------------------------------------------------------------//
// FACTORY -> NG-GRID BASIC SETTINGS
//--------------------------------------------------------------------------------------------//

app.factory('ngGridbasic', function($http){
    scope = this;
    return {
	// GRID OPTIONS
	gridOptions: { 
	    data: 'items',
	    columnDefs: 'myColumnDefs',
	    showGroupPanel: true,
	    jqueryUIDraggable: true,
	    multiSelect: true,
	    keepLastSelected: true,
	    showSelectionCheckbox: true,
	    headerRowHeight: 50,
	    rowHeight: 120,
	    plugins: [new ngGridFlexibleHeightPlugin(),],
	    enablePaging: true,
	    totalServerItems: 'totalServerItems',
	    showFooter: true,
	    primaryKey: 'pk',
	    beforeSelectionChange: function() {
		return scope.enableRowSelection;
	    }  
	},
	// SELECTION OPTIONS
	mySelections : [],
	enableRowSelection: false,
	// FILTER OPTIONS
	searchOptions : {
	    filterText: '',
	    useExternalFilter: true,
	},
	// PAGING OPTIONS
	totalServerItems : 0,
	pagingOptions : {
	    pageSizes: [5, 10, 20, 50, 100],
	    pageSize: 10,
	    currentPage: 1,
	},
	// HTTP GET - FETCH DATA
	preselectItems : function(preselection) {
	    angular.forEach(scope.items, function(data, index){
		if(preselection.indexOf(data.pk) !== -1) {
		    scope.gridOptions.selectedItems.push(data);
		}
	    });
	},
	preselection_data : '',
	updateColumnDefs : function(edit_tools){
	    return edit_tools
	},
	getSelectedItems : function(){
	    var selected = [];
	    scope.mySelections.forEach(function(item){selected.push(item.pk)});  
	    scope.SelectedItemsPks = selected.toString();
	    scope.refresh(scope.get_url);
	},
	refresh : function(get_url) {
	    scope = this;
	    setTimeout(function () {
		var p = {
		    search: scope.searchOptions.filterText,
		    pageNumber: scope.pagingOptions.currentPage,
		    pageSize: scope.pagingOptions.pageSize,
		    items: scope.SelectedItemsPks
		};
		angular.extend(p, scope.filter_data)
		$http({
		    url: get_url,
		    method: "GET",
		    params: p
		}).success(function(data, status, headers, config) {
		    // expects data object: data{'count': 'number_of_objects_in_filtered_queryset', 'objects':objects}
		    scope.totalServerItems = data['count'];
		    scope.items = data['objects'];
		    scope.updateColumnDefs(data['object_edit_tools']);
		    if (data['preselection'] && scope.gridOptions.selectedItems.length == 0) {
			scope.preselectItems(data['preselection']);
		    }
		    scope.SelectedItemsPks = '';
		}).error(function(data, status, headers, config) {
		    alert(JSON.stringify(data));
		});
	    }, 100);
	},
	
	// WATCHES
	setWatches : function(get_url) {
	    scope = this;
	    scope.$watch('pagingOptions', function (newVal, oldVal) {
		if (newVal !== oldVal) {
		    scope.refresh(get_url);
		}
	    }, true);
	    scope.$watch('searchOptions', function (newVal, oldVal) {
		if (newVal !== oldVal) {
		    scope.refresh(get_url);
		}
	    }, true);
	    scope.$watch('forceRefresh', function (newVal, oldVal) {
		if (newVal == true) {
		    scope.refresh(get_url);
		}
	    }, true);
	},
    }     
});

//--------------------------------------------------------------------------------------------//
// CONTROLLER -> RESOURCE LIST 
//--------------------------------------------------------------------------------------------//

app.controller('ResourceListCtrl', function($scope, $http, $location, ngGridbasic, ajaxForm) {
    // ResourceList Fields Templates:
    var thumbnail_temp = '' + 
	'<div class="ngCellText" ng-class="col.colIndex()">' +
	'  <img class="media-object" src="/media/{{row.getProperty(col.field)}}"/>' +
	'</div>';
    var text_temp = '' +
	'<div class="ngCellText" ng-class="col.colIndex()">' +
	'  <span style="font-size:16px">{{row.getProperty(col.field)}}</span>' +
	'</div>';
    var date_temp = '' +
	'<div class="ngCellText" ng-class="col.colIndex()">' +
	'  <span style="font-size:16px">{{row.getProperty(col.field).split(" ")[0]}}</span><br>' +
	'  <span style="font-size:16px">{{row.getProperty(col.field).split(" ")[1]}}</span>' +
	'</div>';
    var type_temp = '' +
	'<div class="ngCellText" ng-class="col.colIndex()">' +
        '<span ng-class="{add_icon_video: row.getProperty(col.field) == \'V\'}"></span>' +
        '<span ng-class="{add_icon_picture: row.getProperty(col.field) == \'I\'}"></span>' +
        '<span ng-class="{add_icon_audio: row.getProperty(col.field) == \'A\'}"></span>' +
	'</div>';
    var detail_temp = '' +
	'<div class="ngCellText" ng-class="col.colIndex()">' +
	'  <a class="" href="/storage/resource/detail/{{row.getProperty(col.field)}}">' +
	'  <i class="icon-zoom-in icon-2x"></i></a>' +
	'</div>';
    var update_temp = '' +
	'<div class="ngCellText" ng-class="col.colIndex()">' +
	'  <a class="" href="#" data-toggle="modal" ng-click="getUpdateAjaxForm(row.entity.pk)">' +
	'  <i class="icon-edit icon-2x"></i></a>' +
	'</div>';
    var delete_temp = '' +
	'<div class="ngCellText" ng-class="col.colIndex()">' +
	'  <a class="" href="/storage/resource/delete/{{row.getProperty(col.field)}}">' +
	'  <i class="icon-remove icon-2x"></i></a>' +
	'</div>';
    var request_temp = '' +
	'<div class="ngCellText" ng-class="col.colIndex()">' +
	'  <a class="" href="/storage/resource/request/{{row.getProperty(col.field)}}">' +
	'  <i class="icon-question icon-2x"></i></a>' +
	'</div>';
    //use 'ngGridbasic' factory to load basic stuff for ng-grid
    angular.extend($scope, ngGridbasic)
    // GRID OPTIONS EXTRA    
    var gridOptionsExtra = { 	  
	pagingOptions: $scope.pagingOptions,
	filterOptions: $scope.searchOptions,
	selectedItems: $scope.mySelections,
    };
    // load grid extra options
    angular.extend($scope.gridOptions, gridOptionsExtra);
    // set columns defs
    $scope.myColumnDefs = [
	{field:'thumbnail_default', displayName:'Thumbnail', width: "110", resizable: false, cellTemplate: '/static/angular/templates/storage/resource_list_thumbnail.html'},
	{field: 'resource_type', displayName: 'Type', cellTemplate: type_temp},
	{field: 'name', displayName: 'Name', cellTemplate: text_temp},
	{field: 'date_recorded', displayName: 'Recorded', cellTemplate: date_temp},
	{field: 'owner__username', displayName: 'Owner', cellTemplate: text_temp},
	{field: 'status', displayName:'status', cellTemplate: text_temp},
	{field: 'pk', displayName:'Detail', cellTemplate: detail_temp},
	{field: 'pk', displayName:'Update', cellTemplate: update_temp},
	{field: 'pk', displayName:'Delete', cellTemplate: delete_temp},
	{field: 'pk', displayName:'Ask for permission', cellTemplate: request_temp},
    ]
    // define updateColumnDefs
    $scope.updateColumnDefs = function(edit_tools) {
	if (edit_tools) { 
	    $scope.myColumnDefs[9]['visible'] = false;
	    $scope.editable = true;
	} else {
	    $scope.myColumnDefs[7]['visible'] = false;
	    $scope.myColumnDefs[8]['visible'] = false;
	}	
    }
    // set get_url
    $scope.get_url = $location.absUrl().replace(/#\/.*/,"")
    // set watches
    $scope.setWatches($scope.get_url);
    // TODO: get rid of it here
    $(document).ready(function() {
	$('#selection_switch').bootstrapSwitch('size', 'mini').on('switchChange', function (e, data) {
	    $scope.enableRowSelection = data.value;
	});
    });
    // refresh grid on load
    $scope.refresh($scope.get_url);
    // modal with item preview
    $scope.modalPreview = {}
    $scope.getModalPreview = function(object) {
	$scope.modalPreview.label = object.name
	$scope.modalPreview.thumbnail = object.thumbnail_large
	$('#modalPreview').modal('show')
    }

    // AJAX FORMS
    angular.extend($scope, ajaxForm)
    // define form div id 
    $scope.form_div = '#modal-form-div'
    $scope.submit_function = ''

    // modal forms GET/POST handlers
    // TODO: do it more DRY, improve 'ajaxForm' factory

    // UPDATE RESOURCE FORM
    $scope.getUpdateAjaxForm = function(pk){
	$scope.getAjaxForm('/storage/resource/update/'+pk, $scope.form_div);
	$scope.modal_form_header = '<i class="icon-edit"></i> Update resource';
	$scope.submit_function = function(){
	    $.when($scope.postAjaxForm('/storage/resource/update/'+pk+'/', $scope['resource_data'], $scope.form_div)).then($scope.refresh($scope.get_url));
	}
	$('#myModal').modal('show')
    }
    // REQUEST FOR RESOURCE FORM
    $scope.getRequestAjaxForm = function(pk){
	$scope.getAjaxForm('/storage/resource/request/'+pk, $scope.form_div);
	//$scope.modal_form_header = '<i class=""></i> Request for resource'
	$scope.submit_function = function(){
	    $scope.postAjaxForm('/storage/resource/request/'+pk+'/', $scope['resource_data'], $scope.form_div);
	}
	$('#myModal').modal('show')
    }
    // CREATE COLLECTION FORM (use selections)
    $scope.getCollectionCreateAjaxForm = function(){ 
	$scope.getAjaxForm('/storage/collection/create', $scope.form_div, true);
	$scope.modal_form_header = '<i class="icon-archive"></i> Create collection'
	// custom POST function to deal with selected rows (here resources in collection)
	$scope.submit_function = function(){
	    var form_data = 'collection_data'
	    $scope[form_data].resources = [];
	    // push selected rows into resources list
	    $scope.mySelections.forEach(function(item){$scope[form_data].resources.push(item.pk)});
	    $scope.postAjaxForm('/storage/collection/create/', $scope[form_data], $scope.form_div);
	}
	$('#myModal').modal('show')
    }
    // UPDATE COLLECTION FORM (use selections)
    $scope.getCollectionUpdateAjaxForm = function(){
	var form_url = $scope.get_url.replace("update","update2")
	$scope.getAjaxForm(form_url, '#collection_update', true);
	// custom POST function to deal with selected rows (here resources in collection)
	$scope.collection_update_submit = function(){
	    var form_data = 'collection_data'
	    $scope[form_data].resources = [];
	    // push selected rows into resources list
	    $scope.mySelections.forEach(function(item){$scope[form_data].resources.push(item.pk)});
	    $scope.postAjaxForm(form_url, $scope[form_data], '#collection_update');
	}
    }
    // ADD COLLECTION TO PROJECT FORM (use selections)
    $scope.getProjectCollectionCreateAjaxForm = function(){ 
	$scope.getAjaxForm('/research/project/collection/create', $scope.form_div);
	$scope.modal_form_header = '<i class="icon-add"></i> Add Collection to Research Project'
	$scope.submit_function = function(){
	    var form_data = 'projectcollection_data';
	    $scope[form_data].collection = $scope.get_url.split('/').slice(-2,-1)[0];
	    $scope.postAjaxForm('/research/project/collection/create/', $scope[form_data], $scope.form_div);
	}
	$('#myModal').modal('show')
    }

});





