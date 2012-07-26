<div class="image">
	<img src="http://placehold.it/225x120" alt="" />
</div>
<div class="title">
	<a href="/projects/<%= slug %>/" class="ajax">
	    <h3><%= title %></h3>
	    <%= location %>
	</a>
</div>

<div class="progressbar">
	<div class="donated-text" style="margin-left: 0px; opacity: 1; ">
		Now: <b>&euro;<span class="donated-amount"><%= money_donated %></span></b>					
	</div>
	<div class="asked-bar">
		<div class="donated-bar" style="width:0px; "></div>
	</div>
	<div class="asked-text">
		Needed: <b>&euro;<span class="asked-amount"><%= money_asked %></span></b>
	</div>
</div>
<div class="support">
	SUPPORT THIS PROJECT
</div>
