fh=$.parseJSON('[["undefined", 1], ["empty", 1],["not sure",1], ["Net Expenses Before Indirect", 1], ["Net Expenses After Indirect", 1], ["Net Investment Income", 1], ["Portfolio Turnover Rate", 1]]');

soo = [["undefined", 1], 
	["empty", 1],
	["not sure",1], 
	["Income", 1], 
		["Interest", 2], 
		["Interest:", 2], 
			["Companies owned (more|less) than X%", 3], 
			["Unspecified", 3], 
		["Dividends", 2], 
		["Dividends:", 2], 
			["Unspecified", 3], 
		["Lease", 2], 
		["Securities lending", 2], 
		["Other income", 2], 
		["Total investment income [Total]", 2], 
	["Expenses", 1], 
		["Total expenses [Total]", 2],
		["Net expenses", 2],		
		["Net investment income / loss", 2],			
		["Accounting", 2], 
		["Administration", 2], 
		["Administration and management", 2],
		["Advisory fees", 2], 
			["Advisory base", 3], 
			["Return including adjustment", 3], 
			["Group fee", 3], 
		["Amortization", 2],
		["Auction fees", 2],
		["Audit", 2],
		["Audit and legal", 2],
		["Audit and accounting", 2],
		["Commitment fees", 2],
		["Compliance officer fees", 2],
		["Custodian", 2],
		["Custodian and accounting", 2],
		["Custody, accounting and administration", 2],
		["Directors fee", 2],
		["Directors/trustee comp", 2],
		["Distribution fees", 2],
		["Distribution and service plan fees", 2],
		["Waivers", 2],
			["Administrator waiver", 3],
			["Advisor waiver", 3],
			["Advisor recoup", 3],
			["Custodian waiver", 3],
			["Combined waiver", 3],
			["Other waiver", 3],
			["Distribution waiver", 3],
		["Indirect Expenses", 2],
			["Indirect transfer agent", 3],
			["Indirect custodian", 3],
			["Indirect soft dollar", 3],
			["Indirect other", 3],
		["Fund accounting", 2],
		["General and administrative", 2],
		["Incentive fees", 2],
		["Insurance", 2],
		["Interest expense", 2],
		["Investment advisory fees", 2],
		["Legal fees", 2],
		["Legal and accounting", 2],
		["Legal fees, professional fees, due diligence expenses", 2],
		["Line of credit", 2],
		["Liquidity fees", 2],
		["Listing fees", 2],
		["Management fees", 2],
		["Marketing and distribution", 2],
		["Management fee to affiliate", 2],
		["Miscellaneous/other", 2],
		["Offering expenses", 2],
		["Organization costs", 2],
		["Payroll", 2],
		["Postage", 2],
		["Preferred shares service fee", 2],
		["Printing, postage, mailings", 2],
		["Professional", 2],
		["Ratings fees", 2],
		["Registration", 2],
		["Remarketing", 2],
		["Remarketing preferred shares", 2],
		["Reorganization", 2],
		["Reports to shareholders", 2],
		["Salaries and Compensation", 2],
		["Shareholder communications", 2],
		["Shareholder expenses", 2],
		["Shareholder meetings", 2],
		["Tax", 2],
		["Transfer and shareholder servicing agent", 2],
		["Trustee compensation", 2],
	["Realized and unrealized gain from investments", 1],
		["Net realized gain (loss) [Total]", 2],
		["Net realized gain (loss) from:", 2],
			["Interest", 3],
			["Dividends", 3],
			["Security transactions", 3],
			["Future contracts", 3],
			["Options on future contracts", 3],
			["Forward contracts", 3],
			["Swaps", 3],
			["Broker commissions", 3],
			["Foreign currency transactions", 3],
			["Investments", 3],
			["Unaffiliated securities", 3],
			["Unspecified", 3],
		["Net change in unrealized appreciation (depreciation) [Total]", 2],
		["Net change in unrealized appreciation (depreciation) on:", 2],
			["Security transactions", 3],
			["Options on future contracts", 3],
			["Future contracts", 3],
			["Forward contracts", 3],
			["Foreign currency", 3],
			["Investments", 3],
			["Swaps", 3],
			["Unaffiliated securities", 3],
			["Unspecified", 3],
		["Net gain (loss) from investments", 2],
		["Net decrease in net assets", 2]];

topLevelItems=soo.filter(function(e){
	// console.log(e);
	return e[1]==1;
});

//On startup: generate full key list (e.g. "Income//Interest" from "Interest" and its sub-item "Income"): 
var key=["","",""];
sooFull=[];
for(var i=0; i<soo.length; i++){
	var item = soo[i];
	key[item[1]-1]=item[0];
	for(var j=item[1]; j<key.length;j++)
		key[j]="";
	var tmp=key[0];
	for(var j=1; j<key.length; j++){
		if(key[j]!="")
			tmp+='//' + key[j];
		else
			break;	
	}
	sooFull.push(tmp);
}

// Generate sub-item list ("Class 1", "Class A", "Investor class", etc)
subClasses=['','not sure','Fund Level', 
	'Affiliated Issuers', 
	'Unaffiliated Issuers', 
	'Admiral Shares',
	'Advisor Class',
	'ETF Shares',
	'Institutional Class', 	
	'Institutional Plus Shares',	
	'Investor Class', 
	'Retail Class', 
	'Retirement Class',
	'Retirement 5 Class', 
	'Retirement 6 Class', 
	'Service Shares', 
	'Non-Service Shares',
	'Signal Shares'
	// TODO: Develop general solution for 'Investor A', 'Investor A1', 'Investor B', 'Retirement 5', 'Retirement 6', etc.
	]

for(var i=1; i<=10; i++)
	subClasses.push('Class ' + i)
var alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");
for(var i=0; i<alphabet.length; i++)
	subClasses.push('Class ' + alphabet[i])



//Get all items sharing the same path as 'item' (aka, the sub-items):
//function getSubItems(item){
//	return sooFull.filter(function(e){return (e.slice(0,item.length)===item) && e.length>item.length});
//}

// add colored borders to table for better testing:
$(function(){
	tableBorders();
	tdBorders();

});

function tdBorders(){
	$('.fh_table td').css({'border':'1px dashed gray'});
	$('.soo_table td').css({'border':'1px dashed gray'});
}

function tableBorders(){

	$('.fh_table').css({'border': '3px solid red'});
	$('.soo_table').css({'border':'3px solid green'});
	$('.fh_table_cont').css({'border':'3px dashed red'});
	$('.soo_table_cont').css({'border':'3px dashed green'});
	$('.sal_table').css({'border':'3px solid blue'});
	$('.sal_table_cont').css({'border':'3px dashed blue'});
	$('.scna_table').css({'border': '3px solid yellow'});
	$('.scna_table_cont').css({'border': '3px dashed yellow'});
	$('.other').css({'border':'1px dashed gray'});
	$('table').not('.fh_table, .soo_table, .fh_table_cont, .soo_table_cont, .sal_table, .sal_table_cont, .scna_table, .scna_table_cont').css({'border':'1px dashed gray'})

};

// table types: 
table_type=		['other',
			'soo_table',           
			'soo_table_cont',                 
			'fh_table',
			'fh_table_cont',
			'sal_table',
			'sal_table_cont',
			'scna_table',
			'scna_table_cont',
			'soo_plus_saa_table'];
table_type_display=	['other',
			'Statement of Operations',
			"Statement of Operations (cont'd)", 
			'Financial Highlights',
			"Financial Highlights (cont'd)",
			"Statement of Assets and Liabilities",
			"Statement of Assets and Liabilities (cont'd)",
			"Statement of Changes in Net Assets",
			"Statement of Changes in Net Assets (cont'd)",
			"Statement of Operations AND Assets and Liabilities"   ];

// add table type select box 
$(function() {
	$('table').each(function(index, elem){
		var attr = $(elem).attr('id');
		if (typeof attr == typeof undefined || attr == false) {
		    $(elem).attr('id', 'ann-table-'+index);
		}
		// if ($(elem).hasAttribute("id") == false) { 
		// 	$(elem).attr('id', 'ann-table-'+index);
		// }
		var key = 'other'
		for(var i=0; i<table_type.length; i++){
			if ($(elem).hasClass(table_type[i])){
				key=table_type[i];
				break;
			}
		}


		if(typeof key === 'undefined') key='other';

		var box = $('<select class="ncsr_table_type" style="margin-left:2em;"></select>');
		for(var i=0; i<table_type.length; i++)
			box.append('<option value="' + table_type[i] + '">Table type: ' + table_type_display[i] + '</option>');
		if($(elem).has("select.ncsr_table_type").length==0){
                        $(elem).append(box);
                }
                else{
                        $(elem).find("select.ncsr_table_type").replaceWith(box);
                }
		box.change(function(ev) {
                        var changedSelectBox = $(ev.target);
                        var selectedValue = changedSelectBox.val();
                        changedSelectBox.parents('table').attr('class', selectedValue);
			tableBorders();
			tdBorders();

			// type change may neccesitate addition of SOO/FH boxes:
			if(selectedValue.startsWith('soo_')){ 
				addSooAnnotationBoxes();
			}
			else if(selectedValue.startsWith('fh_')){
				addFHAnnotationBoxes();
			}
                });
		box.val(key);



	});



});

//Add select box to all first <td> items (row + col) in the financial highlights (FH) table:
$(function() {
 	addFHAnnotationBoxes();
});

function addFHAnnotationBoxes(){

	// <TD>s for first column:			
	var allTDs = $('.fh_table:first      tr td:first-child,' + 
			 '.fh_table_cont:first tr td:first-child')

	// Determine the longest row (first row may be a bad choice
        // as it may be only on <TD> long):
	var tableTypes=['fh_table', 'fh_table_cont'];
	for(var i=0; i<2; i++){
		var tables = document.getElementsByClassName(tableTypes[i]);
		if(tables.length==0){
			console.log('skipping');
			continue
			
		}
		table = tables[0];	
		var j=0, maxRow=0, maxLength=0;
		for (j; j<table.rows.length; j++){
			if(table.rows[j].cells.length>maxLength){
				maxLength=table.rows[j].cells.length;
				maxRow=j;
			}

		}
		console.log(maxRow);
		var TDs = $(table).find('tr:eq(' + maxRow  + ') td');
		allTDs = $.merge(allTDs, TDs);
	}
	
	allTDs.each(function(index, elem) {
	var key = $(elem).attr('fh_label');
	if(typeof key === 'undefined') key='undefined';

	var box = $('<select class="fh_main" style="margin-left:0em;font-size:xx-small;width=50%"></select>');
	for(var i=0; i<fh.length; i++){
		box.append('<option value="' + fh[i][0] + '">' + fh[i][0] + '</option>');
	}
	box.change(function(ev) {
		var changedSelectBox = $(ev.target);
		var selectedValue = changedSelectBox.val();
		changedSelectBox.parents('td').attr('fh_label',selectedValue);
	});
	box.val(key);	
	if($(elem).has("select.fh_main").length==0){
		$(elem).append(box);
	}
	else{
		$(elem).find("select.fh_main").replaceWith(box);
	}
			
	});
};


$(function() {
	addSooAnnotationBoxes();
});
function addSooAnnotationBoxes(){
	$('.soo_table tr td:first-child, .soo_table_cont tr td:first-child').each(function(index, elem) {
		var key = $(elem).attr('soo_label');
		if(typeof key === 'undefined') key='undefined'; 
		var box = createNewLabelingDropdown();
		insertOptions(box,key);

		// There may be a select item or not:
		if($(elem).has("select.soo_main").length==0){
			$(elem).append(box);
		}
		else{
			$(elem).find("select.soo_main").replaceWith(box);
		}
		box.val(key)

		// box for "class items"
		var subBox = createNewSubItemDropdown();
		var key_sec = $(elem).attr('soo_label_sec');
		if(typeof key === 'undefined') key='';
		if($(elem).has("select.soo_sec").length==0){
			$(elem).append(subBox);

		}
		else{
			$(elem).find("select.soo_sec").replaceWith(subBox);

		}
		subBox.val(key_sec);
	});
	 
};

 

//Create sub-item dropdown box
function createNewSubItemDropdown(){
	var subItemDropdown = $('<select class="soo_sec" style="margin-left:2em;"></select>');
	for(var i=0; i<subClasses.length; i++){
		subItemDropdown.append('<option value="' + subClasses[i] + '">' + subClasses[i] + '</option>');
		
	}
	subItemDropdown.change(function(ev){
		var box = $(ev.target);
		var val = box.val();
		box.parents('td').attr('soo_label_sec',val);
	});
	return subItemDropdown;
}

//Create new empty dropdown box
function createNewLabelingDropdown() {

	var labelDropdown = $('<select class="soo_main" style="margin-left:2em;"></select>');

	// Listener to change the attributes of the containing row
	labelDropdown.change(function(ev) {
		var changedSelectBox = $(ev.target);
		var selectedValue = changedSelectBox.val();
		changedSelectBox.parents('td').attr('soo_label', selectedValue);
		var tmp = selectedValue.split('//');

	});
	return labelDropdown;
}

//Insert options depending on section:
var cTopLevel='';
var cSecLevel='';


function insertOptions(selectBox, key){
	for(var i=0; i<sooFull.length; i++){
		var keyParts = sooFull[i].split('//');
		var prefix=''
		var boldStart=''
		var boldEnd=''
		if(keyParts.length==1){
			boldStart='####  '; boldEnd='  ####';
		}	
		for(var j=0; j<keyParts.length-1; j++)
			prefix=prefix+'....';	
		selectBox.append('<option value="' + sooFull[i] + '">' +boldStart+prefix+keyParts[keyParts.length-1]+boldEnd + '</option>');
	}
}


