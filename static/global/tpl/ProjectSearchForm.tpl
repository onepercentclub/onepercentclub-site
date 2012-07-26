<h2>Search Projects</h2>

<form action="/project/search" class="ajax" method="get">
	<input name="title__icontains" />
	<select name="country__contains">
		<option value="">All countries</option>
		<option value="KE">Kenya</option>
		<option value="UG">Uganda</option>
	
	</select>
	<input type="submit" value="Search" />
</form>